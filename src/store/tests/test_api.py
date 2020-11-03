import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from store.models import Book
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

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        serializer_data = BooksSerializer(
            [self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 1000})
        serializer_data = BooksSerializer(
            [self.book_2], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Author1'})
        serializer_data = BooksSerializer(
            [self.book_1, self.book_3], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_ordering_price(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': '-price'})
        serializer_data = BooksSerializer(
            [self.book_3, self.book_2, self.book_1], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer_data)

    def test_get_ordering_author_name(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'author_name'})
        serializer_data = BooksSerializer(
            [self.book_1, self.book_2, self.book_3], many=True).data
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
            code='permission_denied'),}, response.data)

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
