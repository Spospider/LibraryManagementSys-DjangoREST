from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers
from django.utils.timezone import now
from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated

from ..models import Borrow


# Serializer
class BorrowBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['book', 'expected_return_date']

    def validate(self, data):
        user = self.context['request'].user
        book = data['book']
        expected_return_date = data['expected_return_date']
        
        # Ensure user has not borrowed more than 3 books
        borrowed_books_count = Borrow.objects.filter(user=user, return_date__isnull=True).count()
        if borrowed_books_count >= user.max_borrows:
            raise serializers.ValidationError("You can only borrow up to 3 books at a time. Please return a book to borrow a new one.")

        # Ensure expected return date is within the allowed period
        max_borrow_period = now().date() + timedelta(days=user.borrow_max_days)
        if expected_return_date > max_borrow_period:
            raise serializers.ValidationError(f"The return date cannot exceed {user.borrow_max_days} days from today.")

        return data

class ReturnBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['book']

    def validate(self, data):
        user = self.context['request'].user
        book = data['book']

        # Ensure the user is returning a book they have borrowed
        if not Borrow.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("This book is not currently borrowed by the user.")

        return data
    


class CalculatePenaltyView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        borrows = Borrow.objects.filter(user=user, return_date__isnull=True)
        penalties = {}

        for borrow in borrows:
            overdue_days = (now().date() - borrow.expected_return_date).days
            if overdue_days > 0:
                penalties[borrow.book.ISBN] = f'{overdue_days} days overdue'

        if not penalties:
            return Response({'message': 'No overdue books.'}, status=status.HTTP_200_OK)
        return Response(penalties, status=status.HTTP_200_OK)
    


# Endpoint Views 
class BorrowBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BorrowBookSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            borrow = serializer.save(user=request.user, borrow_date=now().date())

            # Send confirmation email
            send_mail(
                'Book Borrowed Successfully',
                f'You have successfully borrowed {borrow.book.name}. Please return it by {borrow.expected_return_date}.',
                'library@example.com',
                [request.user.email],
            )

            # Schedule reminders using celery
            # Inside the BorrowBookView after saving the borrow instance:
            borrow_period = (borrow.expected_return_date - now().date()).days
            reminder_start_days = borrow_period - 3  # Start sending reminders 3 days before the return date

            if reminder_start_days > 0:
                # Calculate the countdown in seconds until the reminders should start
                countdown_time = reminder_start_days * 24 * 60 * 60  # days to seconds

                # Schedule the reminder emails using Celery
                send_reminder_emails.apply_async((borrow.id,), countdown=countdown_time)

            return Response({"message": "Book borrowed successfully"}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ReturnBookSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            borrow = Borrow.objects.get(user=request.user, book=serializer.validated_data['book'], return_date__isnull=True)
            borrow.return_date = now().date()
            borrow.save()

            # Calculate penalty if late
            if borrow.return_date > borrow.expected_return_date:
                days_late = (borrow.return_date - borrow.expected_return_date).days
                penalty = days_late * request.user.penalty_amount
                return Response({"message": f"Book returned successfully. Late by {days_late} days. Penalty incurred: ${penalty}.", "penalty" : penalty})

            return Response({"message": "Book returned successfully"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Tasks
@shared_task
def send_reminder_emails(borrow_id):
    try:
        borrow = Borrow.objects.get(id=borrow_id)
        user = borrow.user
        book = borrow.book

        # Send reminder email
        send_mail(
            'Book Return Reminder',
            f'Dear {user.username},\n\nThis is a reminder that your borrowed book "{book.name}" is due on {borrow.expected_return_date}. Please return it on time to avoid penalties.\n\nThank you!',
            'library@example.com',
            [user.email],
        )

        # Check if the reminder should continue for the next 2 days
        days_remaining = (borrow.expected_return_date - now().date()).days
        if 1 <= days_remaining <= 3 and borrow.return_date is None:
            # Schedule the next reminder for the following day
            send_reminder_emails.apply_async((borrow.id,), countdown=24 * 60 * 60)  # 1 day in seconds

    except Borrow.DoesNotExist:
        pass