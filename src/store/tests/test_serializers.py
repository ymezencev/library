from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test Book 1', price=500)
        book_2 = Book.objects.create(name='Test Book 2', price=1000)
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test Book 1',
                'price': '500.00'
            },
            {
                'id': book_2.id,
                'name': 'Test Book 2',
                'price': '1000.00'
            },
        ]

        self.assertEqual(expected_data, data)