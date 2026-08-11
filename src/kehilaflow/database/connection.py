import sqlite3
from sqlite3 import Connection


def get_connection(database_path: str = "kehilaflow.db") -> Connection:
    connection = sqlite3.connect(
        database_path,
        check_same_thread=False,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables(connection: Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS donors (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            active INTEGER NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            donation_date TEXT NOT NULL,
            campaign TEXT,
            FOREIGN KEY (donor_id) REFERENCES donors(id)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS pledges (
            id TEXT PRIMARY KEY,
            donor_id TEXT NOT NULL,
            amount INTEGER NOT NULL,
            pledge_date TEXT NOT NULL,
            campaign TEXT,
            FOREIGN KEY (donor_id) REFERENCES donors(id)
        )
        """
    )

    connection.commit()
