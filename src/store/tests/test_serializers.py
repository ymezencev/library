from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer, UserBookRelationSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create(username='test_user1', first_name='Ivan',
                                    last_name='One')
        user2 = User.objects.create(username='test_user2', first_name='Anton',
                                    last_name='Two')
        user3 = User.objects.create(username='test_user3', first_name='Ivan',
                                    last_name='Three')

        book_1 = Book.objects.create(name='Test Book 1', price=500,
                                     author_name='Author1', owner=user1)
        book_2 = Book.objects.create(name='Test Book 2', price=1000,
                                     author_name='Author2')

        UserBookRelation.objects.create(user=user1, book=book_1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelation.objects.create(user=user3, book=book_1,
                                                      like=True)
        user_book_3.rate = 4
        user_book_3.save()
        book_1.refresh_from_db()
        UserBookRelation.objects.create(user=user1, book=book_2, like=True, rate=4)
        UserBookRelation.objects.create(user=user2, book=book_2, like=True, rate=3)
        UserBookRelation.objects.create(user=user3, book=book_2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('id')

        data = BooksSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test Book 1',
                'price': '500.00',
                'author_name': 'Author1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'test_user1',
                'readers': [
                    {'first_name': 'Ivan', 'last_name': 'One'},
                    {'first_name': 'Anton', 'last_name': 'Two'},
                    {'first_name': 'Ivan', 'last_name': 'Three'},
                ],
            },
            {
                'id': book_2.id,
                'name': 'Test Book 2',
                'price': '1000.00',
                'author_name': 'Author2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {'first_name': 'Ivan', 'last_name': 'One'},
                    {'first_name': 'Anton', 'last_name': 'Two'},
                    {'first_name': 'Ivan', 'last_name': 'Three'},
                ],
            },
        ]
        print(data)
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
