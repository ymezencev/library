from django.contrib.auth.models import User
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.services.book import set_rating


class BookTestCase(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='test_username1')
        self.user_2 = User.objects.create(username='test_username2')

        self.book_1 = Book.objects.create(name='Test Book 1', price=500,
                                          author_name='Author1')
        UserBookRelation.objects.create(user=self.user_1, book=self.book_1, like=True,
                                        rate=5)
        UserBookRelation.objects.create(user=self.user_2, book=self.book_1, like=True,
                                        rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.50', str(self.book_1.rating))
