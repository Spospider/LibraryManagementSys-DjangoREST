from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.utils.timezone import now


# Create your models here.
class User(AbstractUser): # extend default django user model
    max_borrows = models.IntegerField(default=3)
    restricted = models.BooleanField(default=False)
    location_lat = models.FloatField(default=100.0) # for calc distances between user and nearest library branch
    location_long = models.FloatField(default=100.0)
    penalty_amount = models.FloatField(default=5.0)
    borrow_max_days = models.IntegerField(default=30)

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Change related_name to avoid conflict
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # Change related_name to avoid conflict
        blank=True
    )

class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Book(models.Model):
    ISBN = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    authors = models.ManyToManyField('Author', related_name='books')
    category = models.CharField(max_length=100, db_index=True)

class Library(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
class LibraryBranch(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    location_lat = models.FloatField()
    location_long = models.FloatField()
    address = models.CharField(max_length=250)

# New intermediate model to track the number of books at each branch
class BookStock(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    library_branch = models.ForeignKey(LibraryBranch, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)  # Number of copies of the book at the branch

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    borrow_date = models.DateField()
    expected_return_date = models.DateField() # add validation to assign this > today's date?
    return_date = models.DateField(null=True, blank=True)

    def clean(self): # for expected_return_date validation
        if self.expected_return_date <= now().date():
            raise ValidationError("Expected return date must be in the future.")
        
        # Validate that the return date is after the borrow date
        if self.return_date and self.return_date <= self.borrow_date:
            raise ValidationError("Return date must be after the borrow date.")