from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, serializers
from geopy.distance import geodesic
# from ..serializers import LibrarySerializer, LoadedAuthorSerializer, AuthorSerializer, BookSerializer
from django.db.models import Count
from math import radians, sin, cos, sqrt, atan2
from ..models import Author, Book, LibraryBranch, Library, Book, BookStock


class LibraryBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryBranch
        fields = ['library', 'location_lat', 'location_long', 'address']
    def get_distance(self, obj):
        user = self.context.get('user')
        if user:
            if obj:
                user_location = (user.location_lat, user.location_long)
                branch_location = (obj.location_lat, obj.location_long)
                distance = geodesic(user_location, branch_location).km
                return round(distance, 2)
        return None


class LibrarySerializer(serializers.ModelSerializer):
    branches = LibraryBranchSerializer(many=True)
    
    class Meta:
        model = Library
        fields = ['name', 'branches']


class LibraryListSerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField()
    num_branches = serializers.SerializerMethodField()

    class Meta:
        model = Library
        fields = ['name', 'num_branches','distance']
    def get_distance(self, obj):
        user = self.context.get('user')
        if user:
            closest_branch = obj.librarybranch_set.all().first()
            if closest_branch:
                user_location = (user.location_lat, user.location_long)
                branch_location = (closest_branch.location_lat, closest_branch.location_long)
                distance = geodesic(user_location, branch_location).km
                return round(distance, 2)
        return None
    def get_num_branches(self, obj):
        return obj.librarybranch_set.count()

# View for Library Management
class LibraryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Filtering by book categories, authors, and optional distance calculation
        category_filter = request.GET.get('category')
        author_filter = request.GET.get('author')
        user = request.user

        libraries = Library.objects.all()

        if category_filter:
            # books = Book.objects.filter(category=category_filter)
            # branch_ids = BookStock.objects.filter(book__in=books).values_list('library_branch', flat=True).distinct()
            # libraries = libraries.filter(librarybranch__id__in=branch_ids)

            libraries = libraries.filter(librarybranch__bookstock__book__category=category_filter)
        
        if author_filter:
            # authors = Author.objects.filter(name=author_filter)
            # books = Book.objects.filter(authors__in=authors)
            # branch_ids = BookStock.objects.filter(book__in=books).values_list('library_branch', flat=True).distinct()
            # libraries = libraries.filter(librarybranch__id__in=branch_ids)

            libraries = libraries.filter(librarybranch__bookstock__book__authors__name=author_filter)

        # Serialize the libraries with distance data
        serializer = LibraryListSerializer(libraries, many=True, context={'user': user})

        return Response(serializer.data)




## Authors
class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['name', 'book_count']
    
    def get_book_count(self, obj):
        # Count the number of books for each author
        return obj.books.count()


class AuthorListSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['name', 'book_count']

    def get_book_count(self, obj):
        # Return the count of books written by the author
        return obj.books.count()
    
# View for Authors
class AuthorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get filters for library and book category
        library_filter = request.GET.get('library')
        category_filter = request.GET.get('category')

        authors = Author.objects.all()

        if library_filter:
            # Filter by library: authors whose books are in the given library
            authors = authors.filter(
                book__bookstock__library_branch__library__name=library_filter
            ).distinct()

        if category_filter:
            # Filter by book category: authors whose books are in the given category
            books_in_category = Book.objects.filter(category=category_filter)
            authors = authors.filter(book__in=books_in_category)

        # Serialize the authors with book count
        serializer = AuthorListSerializer(authors, many=True)

        return Response(serializer.data)


## Books
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['name']

class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Book
        fields = ['ISBN', 'name', 'category', 'authors']

# View for books endpoint
class BookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get filters for category, library, and author
        category_filter = request.GET.get('category')
        library_filter = request.GET.get('library')
        author_filter = request.GET.get('author')

        books = Book.objects.all()

        if category_filter:
            # Filter by book category
            books = books.filter(category=category_filter)

        if library_filter:
            # Filter by library: books available in a specific library
            try:
                books = books.filter(bookstock__library_branch__library__name=library_filter)
            except LibraryBranch.DoesNotExist:
                return Response({"error": "Library branch not found"}, status=404)

        if author_filter:
            # Filter by author: books written by a specific author
            try:
                author = Author.objects.get(name=author_filter)
                books = books.filter(authors=author)
            except Author.DoesNotExist:
                return Response({"error": "Author not found"}, status=404)

        # Serialize the books with their authors' names
        serializer = BookSerializer(books, many=True)

        return Response(serializer.data)


## Loaded Authors Endpoint
class AuthorWithBooksSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)  # List of books the author has written
    
    class Meta:
        model = Author
        fields = ['name', 'books']

class LoadedAuthorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get filters for category and library
        category_filter = request.GET.get('category')
        library_filter = request.GET.get('library')

        authors = Author.objects.all()

        if category_filter:
            # Filter by book category: authors who have books in the specified category
            books_in_category = Book.objects.filter(category=category_filter)
            authors = authors.filter(book__in=books_in_category)

        if library_filter:
            # Filter by library: authors who have books available in a specific library
            try:
                authors = authors.filter(
                    book__bookstock__library_branch__library__name=library_filter
                ).distinct()
            except LibraryBranch.DoesNotExist:
                return Response({"error": "Library branch not found"}, status=404)            

        # Serialize the authors with their books and associated libraries
        serializer = AuthorWithBooksSerializer(authors, many=True)

        return Response(serializer.data)


