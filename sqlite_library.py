"""SQLite tables, deletion, and cached queries for laboratory work № 7."""

import sqlite3
from functools import lru_cache


class Library:
    def __init__(self, database=":memory:"):
        self.connection = sqlite3.connect(database)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                author_id INTEGER NOT NULL REFERENCES authors(id)
            );
        """)

    def add_author(self, name):
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO authors(name) VALUES (?)", (name,))
        return cursor.lastrowid

    def add_book(self, title, author_id):
        with self.connection:
            cursor = self.connection.execute(
                "INSERT INTO books(title, author_id) VALUES (?, ?)",
                (title, author_id))
        self.get_book.cache_clear()
        return cursor.lastrowid

    @lru_cache(maxsize=128)
    def get_book(self, book_id):
        """Cache one joined query by book id; return None if absent."""
        row = self.connection.execute("""
            SELECT books.id, books.title, authors.name AS author
            FROM books JOIN authors ON books.author_id = authors.id
            WHERE books.id = ?
        """, (book_id,)).fetchone()
        return dict(row) if row is not None else None

    def delete_book(self, book_id):
        with self.connection:
            cursor = self.connection.execute("DELETE FROM books WHERE id = ?", (book_id,))
        if cursor.rowcount:
            self.get_book.cache_clear()
        return bool(cursor.rowcount)

    def list_authors(self):
        return [dict(row) for row in self.connection.execute(
            "SELECT id, name FROM authors ORDER BY id")]

    def close(self):
        self.get_book.cache_clear()
        self.connection.close()


if __name__ == "__main__":
    library = Library()
    author = library.add_author("А. С. Пушкин")
    book = library.add_book("Капитанская дочка", author)
    print("Авторы:", library.list_authors())
    print("Книга:", library.get_book(book))
    print("Удалена:", library.delete_book(book))
    print("После удаления:", library.get_book(book))
    library.close()
