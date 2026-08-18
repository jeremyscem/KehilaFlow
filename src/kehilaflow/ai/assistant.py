import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4

import anthropic
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import kehilaflow.ai.tools  # noqa: F401
from kehilaflow.ai.registry import (
    execute_tool,
    get_registered_tool,
    get_tool_schemas,
)
from kehilaflow.api.schemas.ai import (
    AIChatHistoryMessage,
)
from kehilaflow.database.tables import (
    AIActionExecutionTable,
)
from kehilaflow.repositories.campaign_repository import (
    CampaignRepository,
)
from kehilaflow.repositories.donor_repository import (
    DonorRepository,
)

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ACTION_SECRET = os.environ["AI_ACTION_SECRET"]

ACTION_TTL_SECONDS = 1800


SYSTEM_PROMPT = """
You are the KehilaFlow admin assistant.

KehilaFlow manages donors, pledges, donations and campaigns.

Use the available tools whenever a question depends on KehilaFlow data.

Never invent financial data.

If the admin mentions a donor by name and you do not know their ID,
use search_donors first.

The conversation history is important.

Always understand short follow-up messages in the context of the previous
conversation.

Examples:

Admin:
How much does Taieb owe?

Assistant:
I found several Taieb donors. Which one?

Admin:
Ilan

You must understand that "Ilan" means "Ilan Taieb".

Other contextual follow-ups include:

"And Mikael?"
"How much did he pay?"
"And for Kippour?"
"yes"
"the second one"
"him"
"same for Jonathan"

If multiple donors are genuinely possible, ask for clarification.
Never arbitrarily choose between ambiguous donors.

WRITE ACTIONS:

Write tools create or modify KehilaFlow data.

When the admin asks to create a donor, pledge, donation/payment
or campaign, first gather all required information using read tools.

Never invent a donor ID or campaign ID.
Use read tools to resolve them.

Never invent a date.
If a required date is missing, ask the admin for it.

When all required information is known, call exactly ONE
appropriate write tool.

The backend will NOT execute the write immediately.
It will prepare the action and ask the admin for confirmation.

Never claim that a write succeeded before the backend returns
a successful write result.

Keep answers concise and practical.

Answer in the language used by the admin whenever possible.

Amounts are in Israeli shekels (₪).
"""


@dataclass
class AIResult:
    answer: str
    pending_action_token: str | None = None


# ------------------------------------------------------------------
# ACTION TOKEN
# ------------------------------------------------------------------


def _encode_base64(
    value: bytes,
) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode_base64(
    value: str,
) -> bytes:
    padding = "=" * (-len(value) % 4)

    return base64.urlsafe_b64decode(value + padding)


def _create_action_token(
    tool_name: str,
    tool_input: dict,
) -> str:
    payload = {
        "action_id": str(uuid4()),
        "tool_name": tool_name,
        "tool_input": tool_input,
        "expires_at": (int(time.time()) + ACTION_TTL_SECONDS),
    }

    payload_bytes = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()

    encoded_payload = _encode_base64(payload_bytes)

    signature = hmac.new(
        ACTION_SECRET.encode(),
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()

    encoded_signature = _encode_base64(signature)

    return f"{encoded_payload}.{encoded_signature}"


def _read_action_token(
    token: str,
) -> dict[str, Any]:
    try:
        (
            encoded_payload,
            encoded_signature,
        ) = token.split(
            ".",
            maxsplit=1,
        )
    except ValueError as error:
        raise ValueError("Invalid confirmation token.") from error

    try:
        received_signature = _decode_base64(encoded_signature)
    except (
        ValueError,
        binascii.Error,
    ) as error:
        raise ValueError("Invalid confirmation token.") from error

    expected_signature = hmac.new(
        ACTION_SECRET.encode(),
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(
        expected_signature,
        received_signature,
    ):
        raise ValueError("Invalid confirmation token.")

    try:
        payload_bytes = _decode_base64(encoded_payload)

        payload = json.loads(payload_bytes)
    except (
        ValueError,
        binascii.Error,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ) as error:
        raise ValueError("Invalid confirmation token.") from error

    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError("Invalid confirmation token.")

    expires_at = payload.get("expires_at")

    if not isinstance(
        expires_at,
        int,
    ):
        raise TypeError("Invalid confirmation token.")

    if expires_at < time.time():
        raise ValueError("Confirmation expired.")

    action_id = payload.get("action_id")

    tool_name = payload.get("tool_name")

    tool_input = payload.get("tool_input")

    if (
        not isinstance(
            action_id,
            str,
        )
        or not isinstance(
            tool_name,
            str,
        )
        or not isinstance(
            tool_input,
            dict,
        )
    ):
        raise TypeError("Invalid confirmation token.")

    return {
        "action_id": action_id,
        "tool_name": tool_name,
        "tool_input": tool_input,
    }


# ------------------------------------------------------------------
# CONFIRM / CANCEL
# ------------------------------------------------------------------


def _normalize_answer(
    message: str,
) -> str:
    value = message.strip().casefold()

    value = re.sub(
        r"[^\w\u0590-\u05ff]+",
        " ",
        value,
    )

    return " ".join(value.split())


def _is_confirmation(
    message: str,
) -> bool:
    value = _normalize_answer(message)

    confirmations = {
        "yes",
        "yes please",
        "oui",
        "oui confirme",
        "oui vas y",
        "ok",
        "okay",
        "confirm",
        "confirme",
        "je confirme",
        "vas y",
        "go",
        "go ahead",
        "do it",
        "כן",
        "מאשר",
        "אישור",
    }

    return value in confirmations


def _is_cancellation(
    message: str,
) -> bool:
    value = _normalize_answer(message)

    cancellations = {
        "no",
        "non",
        "annule",
        "annuler",
        "cancel",
        "cancel it",
        "לא",
        "בטל",
    }

    return value in cancellations


# ------------------------------------------------------------------
# DISPLAY HELPERS
# ------------------------------------------------------------------


def _get_donor_name(
    donor_id: str,
    session: Session,
) -> str:
    try:
        donor_uuid = UUID(donor_id)
    except ValueError:
        return donor_id

    donor = DonorRepository(session).find_by_id(donor_uuid)

    if donor is None:
        return donor_id

    return f"{donor.first_name} {donor.last_name}"


def _get_campaign_name(
    campaign_id: str | None,
    session: Session,
) -> str | None:
    if not campaign_id:
        return None

    try:
        campaign_uuid = UUID(campaign_id)
    except ValueError:
        return campaign_id

    campaign = CampaignRepository(session).find_by_id(campaign_uuid)

    if campaign is None:
        return campaign_id

    return campaign.name


def _describe_write_action(
    tool_name: str,
    tool_input: dict,
    session: Session,
) -> str:
    if tool_name == "register_donation":
        donor_name = _get_donor_name(
            tool_input["donor_id"],
            session,
        )

        campaign_name = _get_campaign_name(
            tool_input.get("campaign_id"),
            session,
        )

        lines = [
            "Je vais enregistrer ce paiement :",
            "",
            (f"- Donateur : **{donor_name}**"),
            (f"- Montant : **{tool_input['amount']} ₪**"),
            (f"- Date : **{tool_input['donation_date']}**"),
        ]

        if campaign_name:
            lines.append(f"- Campagne : **{campaign_name}**")

        lines.extend(
            [
                "",
                "Confirmer ?",
            ]
        )

        return "\n".join(lines)

    if tool_name == "create_pledge":
        donor_name = _get_donor_name(
            tool_input["donor_id"],
            session,
        )

        campaign_name = _get_campaign_name(
            tool_input.get("campaign_id"),
            session,
        )

        lines = [
            "Je vais enregistrer cette promesse :",
            "",
            (f"- Donateur : **{donor_name}**"),
            (f"- Montant : **{tool_input['amount']} ₪**"),
            (f"- Date : **{tool_input['pledge_date']}**"),
        ]

        if campaign_name:
            lines.append(f"- Campagne : **{campaign_name}**")

        lines.extend(
            [
                "",
                "Confirmer ?",
            ]
        )

        return "\n".join(lines)

    if tool_name == "create_donor":
        return (
            "Je vais créer ce donateur :\n\n"
            "- Prénom : "
            f"**{tool_input['first_name']}**\n"
            "- Nom : "
            f"**{tool_input['last_name']}**\n"
            "- Email : "
            f"**{tool_input['email']}**\n"
            "- Téléphone : "
            f"**{tool_input.get('phone') or '-'}**\n\n"
            "Confirmer ?"
        )

    if tool_name == "create_campaign":
        return (
            "Je vais créer cette campagne :\n\n"
            "- Nom : "
            f"**{tool_input['name']}**\n"
            "- Objectif : "
            f"**{tool_input.get('target_amount', 0)} ₪**\n\n"
            "Confirmer ?"
        )

    return "Je suis prêt à effectuer cette modification.\n\nConfirmer ?"


def _describe_write_result(
    tool_name: str,
    tool_input: dict,
    session: Session,
) -> str:
    if tool_name == "register_donation":
        donor_name = _get_donor_name(
            tool_input["donor_id"],
            session,
        )

        return (
            "✅ Paiement de "
            f"**{tool_input['amount']} ₪** "
            "enregistré pour "
            f"**{donor_name}**."
        )

    if tool_name == "create_pledge":
        donor_name = _get_donor_name(
            tool_input["donor_id"],
            session,
        )

        return (
            "✅ Promesse de "
            f"**{tool_input['amount']} ₪** "
            "enregistrée pour "
            f"**{donor_name}**."
        )

    if tool_name == "create_donor":
        return (
            "✅ Donateur "
            f"**{tool_input['first_name']} "
            f"{tool_input['last_name']}** "
            "créé."
        )

    if tool_name == "create_campaign":
        return f"✅ Campagne **{tool_input['name']}** créée."

    return "✅ Modification enregistrée."


# ------------------------------------------------------------------
# EXECUTE CONFIRMED WRITE
# ------------------------------------------------------------------


def _execute_confirmed_action(
    token: str,
    session: Session,
) -> AIResult:
    try:
        action = _read_action_token(token)

        action_id = action["action_id"]

        tool_name = action["tool_name"]

        tool_input = action["tool_input"]

        registered_tool = get_registered_tool(tool_name)

        if not registered_tool.write:
            return AIResult(answer=("Cette action n'est pas une modification valide."))

        # Reserve this action ID before executing
        # the write.
        #
        # action_id is the primary key, so a second
        # request using the same confirmation token
        # will fail here.
        session.add(AIActionExecutionTable(action_id=action_id))

        try:
            session.flush()
        except IntegrityError:
            session.rollback()

            return AIResult(answer=("Cette action a déjà été confirmée."))

        execute_tool(
            name=tool_name,
            tool_input=tool_input,
            session=session,
            allow_writes=True,
        )

        answer = _describe_write_result(
            tool_name,
            tool_input,
            session,
        )

        # The action marker and the business write
        # are committed together.
        session.commit()

        return AIResult(answer=answer)

    except (
        ValueError,
        TypeError,
        KeyError,
    ) as error:
        session.rollback()

        return AIResult(answer=(f"Impossible d'exécuter l'action : {error}"))

    except Exception:
        session.rollback()
        raise


# ------------------------------------------------------------------
# CLAUDE
# ------------------------------------------------------------------


def ask_claude(
    message: str,
    session: Session,
    history: (list[AIChatHistoryMessage] | None) = None,
    pending_action_token: (str | None) = None,
    allow_writes: bool = False,
) -> AIResult:
    # A pending write can only be executed
    # through an explicit confirmation.
    if pending_action_token:
        if _is_confirmation(message):
            return _execute_confirmed_action(
                pending_action_token,
                session,
            )

        if _is_cancellation(message):
            return AIResult(answer="Action annulée.")

        # Any other message means the admin is
        # changing/correcting the request.
        # The previous pending action is abandoned.

    tools = get_tool_schemas(allow_writes=allow_writes)

    messages: list[dict] = []

    if history:
        for history_message in history[-20:]:
            messages.append(
                {
                    "role": (history_message.role),
                    "content": (history_message.content),
                }
            )

    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    for _ in range(10):
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages,
        )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        tool_calls = [block for block in response.content if block.type == "tool_use"]

        if not tool_calls:
            answer = "".join(
                block.text for block in response.content if block.type == "text"
            )

            return AIResult(answer=answer)

        write_calls = []

        for tool_call in tool_calls:
            registered_tool = get_registered_tool(tool_call.name)

            if registered_tool.write:
                write_calls.append(tool_call)

        # Write tools are NEVER executed here.
        # We only generate a signed pending action.
        if write_calls:
            if len(write_calls) > 1:
                return AIResult(
                    answer=("Je ne peux préparer qu'une modification à la fois.")
                )

            write_call = write_calls[0]

            token = _create_action_token(
                write_call.name,
                write_call.input,
            )

            description = _describe_write_action(
                write_call.name,
                write_call.input,
                session,
            )

            return AIResult(
                answer=description,
                pending_action_token=token,
            )

        # Read tools can execute immediately.
        tool_results = []

        for tool_call in tool_calls:
            try:
                result = execute_tool(
                    name=tool_call.name,
                    tool_input=(tool_call.input),
                    session=session,
                    allow_writes=False,
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": (tool_call.id),
                        "content": json.dumps(
                            result,
                            ensure_ascii=False,
                        ),
                    }
                )

            except (
                ValueError,
                TypeError,
                KeyError,
            ) as error:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": (tool_call.id),
                        "is_error": True,
                        "content": str(error),
                    }
                )

        messages.append(
            {
                "role": "user",
                "content": tool_results,
            }
        )

    return AIResult(answer=("The AI assistant reached its tool-call limit."))
