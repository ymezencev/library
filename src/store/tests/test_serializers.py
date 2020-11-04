from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer, UserBookRelationSerializer


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
                'owner': None,
                'readers': []
            },
            {
                'id': book_2.id,
                'name': 'Test Book 2',
                'price': '1000.00',
                'author_name': 'Author2',
                'owner': None,
                'readers': []
            },
        ]
        self.assertEqual(expected_data, data)


class UserBookRelationSerializerTestCase(TestCase):
    def test_ok(self):
        user = User.objects.create(username='user_test')
        book_1 = Book.objects.create(name='Test Book 1', price=500,
                                     author_name='Author1')
        relation = UserBookRelation.objects.create(user=user, book=book_1,
                                                   like=True,
                                                   in_bookmarks=True, rate=3)
        data = UserBookRelationSerializer(relation).data
        expected_data = {
            'book': book_1.id,
            'like': True,
            'in_bookmarks': True,
            'rate': 3,
        }

        self.assertEqual(expected_data, data)
