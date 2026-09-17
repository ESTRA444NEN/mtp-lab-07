import unittest
from unittest.mock import MagicMock

from postgres_library import add_note, delete_note
from sqlite_library import Library


class Lab7Tests(unittest.TestCase):
    def test_sqlite_tables_deletion_and_cache(self):
        library = Library()
        try:
            author = library.add_author("А. С. Пушкин")
            book = library.add_book("Капитанская дочка", author)
            self.assertEqual(library.list_authors()[0]["name"], "А. С. Пушкин")
            self.assertEqual(library.get_book(book)["author"], "А. С. Пушкин")
            library.get_book(book)
            self.assertGreater(library.get_book.cache_info().hits, 0)
            self.assertTrue(library.delete_book(book))
            self.assertIsNone(library.get_book(book))
            self.assertFalse(library.delete_book(book))
        finally:
            library.close()

    def test_postgres_uses_parameters(self):
        connection = MagicMock()
        cursor = connection.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (12,)
        self.assertEqual(add_note(connection, "текст'; DROP TABLE x; --"), 12)
        query, params = cursor.execute.call_args.args
        self.assertIn("%s", query)
        self.assertEqual(params, ("текст'; DROP TABLE x; --",))
        cursor.rowcount = 1
        self.assertTrue(delete_note(connection, 12))


if __name__ == "__main__":
    unittest.main()
