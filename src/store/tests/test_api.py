import json

from django.contrib.auth.models import User
from django.db.models import When, Case, Count, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test Book 1', price=500,
                                          author_name='Author1')
        self.book_2 = Book.objects.create(name='Test Book 2', price=1000,
                                          author_name='Author2')
        self.book_3 = Book.objects.create(name='Test Book 3 Author1',
                                          price=2000,
                                          author_name='Author3',
                                          owner=self.user)

        UserBookRelation.objects.create(user=self.user, book=self.book_1, like=True,
                                        rate=5)

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '5.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 1000})
        books = Book.objects.filter(id__in=[self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('id')

        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author1'})
        books = Book.objects.filter(
            id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_ordering_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('-price')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_ordering_author_name(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(
                userbookrelation__like=True, then=1)))).order_by('author_name')
        serializer_data = BooksSerializer(books, many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
            'name': 'Test Book 4',
            'price': 2500,
            'author_name': 'Author4'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_3.id,))
        data = {
            'name': self.book_3.name,
            'price': 100,
            'author_name': self.book_3.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_3.refresh_from_db()
        self.assertEquals(100, self.book_3.price)

    def test_update_not_owner(self):
        user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_3.id,))
        data = {
            'name': self.book_3.name,
            'price': 100,
            'author_name': self.book_3.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual({'detail': ErrorDetail(
            string='You do not have permission to perform this action.',
            code='permission_denied'), }, response.data)

    def test_update_not_owner_but_staff(self):
        user2 = User.objects.create(username='test_username2', is_staff=True)
        url = reverse('book-detail', args=(self.book_3.id,))
        data = {
            'name': self.book_3.name,
            'price': 100,
            'author_name': self.book_3.author_name
        }
        json_data = json.dumps(data)
        self.client.force_login(user2)
        response = self.client.put(url, data=json_data,
                                   content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_3.refresh_from_db()
        self.assertEquals(100, self.book_3.price)

    def test_delete(self):
        url = reverse('book-detail', args=(self.book_3.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEquals(2, Book.objects.all().count())


class BooksRelationApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_username1')
        self.user2 = User.objects.create(username='test_username2')

        self.book_1 = Book.objects.create(name='Test Book 1', price=500,
                                          author_name='Author1')
        self.book_2 = Book.objects.create(name='Test Book 2', price=1000,
                                          author_name='Author2')

    def test_like(self):
        data = {
            'like': True,
        }
        json_data = json.dumps(data)
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        data = {
            'in_bookmarks': True,
        }
        json_data = json.dumps(data)
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        data = {
            'rate': 5,
        }
        json_data = json.dumps(data)
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(5, relation.rate)

    def test_rate_wrong(self):
        data = {
            'rate': 100,
        }
        json_data = json.dumps(data)
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data,
                                     content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'rate': [
            ErrorDetail(string=f'"{data["rate"]}" is not a valid choice.',
                        code='invalid_choice')]}, response.data)
