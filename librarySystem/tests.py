from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now, timedelta
from librarySystem.models import User, Library, LibraryBranch, Author, Book, BookStock, Borrow

class LibrarySystemTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'Testpass123!',
            'password_confirm' : 'Testpass123!',
            'email': 'testuser@example.com',
            'max_borrows': 3,
            'location_lat': 40.7128,
            'location_long': -74.0060,
            'borrow_max_days': 30,
            'penalty_amount': 5.00
        }
        # self.user = User.objects.create_user(**self.user_data)
        self.library = Library.objects.create(name="Central Library")
        self.branch = LibraryBranch.objects.create(
            library=self.library,
            location_lat=40.7128,
            location_long=-74.0060,
            address="123 Library St"
        )
        self.author = Author.objects.create(name="Author One")
        self.book = Book.objects.create(ISBN="12345", name="Book One", category="Fiction")
        self.book.authors.add(self.author)
        self.book_stock = BookStock.objects.create(book=self.book, library_branch=self.branch, count=10)
        self.borrow_data = {
            'book': self.book.id,
            'expected_return_date': (now().date() + timedelta(days=30)).isoformat()
        }

        # Register user
        response = self.client.post('/api/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user(self):
        user_data = {
            'username': 'testuser1',
            'password': 'Testpass123!',
            'password_confirm' : 'Testpass123!',
            'email': 'testuser1@example.com',
            'max_borrows': 3,
            'location_lat': 40.7128,
            'location_long': -74.0060,
            'borrow_max_days': 30,
            'penalty_amount': 5.00
        }
        response = self.client.post('/api/register/', user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('token', response.data)

    def test_login_user(self):
        response = self.client.post('/api/login/', {'username': 'testuser', 'password': 'Testpass123!'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.access_token = response.data['access_token']

    def test_browse_libraries(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get('/api/libraries/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_browse_authors(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get('/api/authors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_browse_books(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_browse_loaded_authors(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.get('/api/authors/full')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_borrow_book(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        response = self.client.post('/api/borrow/', self.borrow_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)

    def test_return_book(self):
        self.test_login_user()
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
        self.client.post('/api/borrow/', self.borrow_data, format='json')

        return_data = {'book': self.book.id}
        response = self.client.post('/api/return/', return_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)