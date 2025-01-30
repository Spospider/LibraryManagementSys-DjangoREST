from django.urls import path
from django.contrib.auth import views as auth_views
from .views import library, base, borrows, user

urlpatterns = [
    # Library Management
    path('libraries/', library.LibraryListView.as_view(), name='library-list'), 
    # List all libraries
    # ability to filter by get params (by book categories, authors)
    # include distances between users and nearby libraries 

    # Author Management
    path('authors/', library.AuthorListView.as_view(), name='author-list'),  
    # List all authors with book count
    # Ability to filter bylibrary and book category

    # Book Management
    path('books/', library.BookListView.as_view(), name='book-list'),  
    # List all books
    # ability to filter by category, library, and author
    # results contain author 

    # Loaded Authors
    path('authors/full', library.LoadedAuthorListView.as_view(), name='author-loaded-list'),  
    # List all authors with their book objects
    # Ability to filter by category and library

    # Borrowing Books
    path('borrow/', borrows.BorrowBookView.as_view(), name='borrow-book'),  # Borrow a book
    path('return/', borrows.ReturnBookView.as_view(), name='return-book'),  # Return a borrowed book
    # endpoints for borrowing and returning books in the library management systems, there are some business rules:
    # Allow up to 3 books; return one to borrow a 4th
    # Users must specify a return date (max 1 month); late returns incur a daily penalty
    # Send confirmation emails upon borrowing
    # Schedule to Send daily reminders in the last 3 days of the borrowing period

    # User
    path('register/', user.UserRegisterView.as_view(), name='register'),
    path('login/', user.UserLoginView.as_view(), name='login'),

    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]