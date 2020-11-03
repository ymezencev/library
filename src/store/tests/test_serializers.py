from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test Book 1', price=500,
                                     author_name='Author1')
        book_2 = Book.objects.create(name='Test Book 2', price=1000,
                                     author_name='Author2')
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test Book 1',
                'price': '500.00',
                'author_name': 'Author1',
                'owner': None
            },
            {
                'id': book_2.id,
                'name': 'Test Book 2',
                'price': '1000.00',
                'author_name': 'Author2',
                'owner': None
            },
        ]

        self.assertEqual(expected_data, data)
