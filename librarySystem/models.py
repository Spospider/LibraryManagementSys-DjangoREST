from django.db import models

# Create your models here.
class User(models.Model): # extend default django user model
    maxBorrows = models.IntegerField(default=3)
    restricted = models.BooleanField(default=False)

class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    ISBN = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    author = models.ManyToOneRel(Author.name) # foreign key, what if we have multiple authors
    category = models.CharField(max_length=100)

class Library(models.Model):
    name = models.CharField(max_length=100)
    
class LibraryBranch(models.Model):
    library = models.ForeignKey(Library)
    locationLat = models.FloatField() # coordinates?
    locationLong = models.FloatField()

class LibraryBooks(models.Model):
    ISBN = models.ForeignKey(Book.ISBN)
    libraryBranch = models.ForeignKey(LibraryBranch)

class BookAuthors(models.Model):
    authorName = models.ForeignKey(Author.name)
    ISBN = models.ForeignKey(Book.ISBN)

class Borrow(models.Model):
    user = models.ForeignKey(User.email)

class BorrowTransaction(models.Model):
    user = models.ForeignKey(User)
    ISBN = models.ForeignKey(Book)
    returnDate = models.DateField() # add validation to assign this > today's date?