"""Повышенное задание № 6: PostgreSQL через psycopg2."""

import os


def create_table(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lab7_notes (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    text TEXT NOT NULL
                )
            """)


def add_note(connection, text):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO lab7_notes(text) VALUES (%s) RETURNING id", (text,))
            return cursor.fetchone()[0]


def list_notes(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, text FROM lab7_notes ORDER BY id")
        return cursor.fetchall()


def delete_note(connection, note_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM lab7_notes WHERE id = %s", (note_id,))
            return cursor.rowcount > 0


def main():
    import psycopg2

    dsn = os.environ.get("LAB7_PG_DSN")
    if not dsn:
        raise SystemExit("Задайте LAB7_PG_DSN для подключения к PostgreSQL")
    connection = psycopg2.connect(dsn)
    try:
        create_table(connection)
        note_id = add_note(connection, "Демонстрационная запись")
        print("Записи:", list_notes(connection))
        print("Удалена:", delete_note(connection, note_id))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
