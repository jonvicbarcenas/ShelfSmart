"""Email notification utilities for due and overdue book reminders"""

from datetime import date, timedelta
from typing import List, Dict, Any
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from admin.common.models import BorrowRecord
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def send_due_reminder_email(user_email: str, user_name: str, book_title: str, due_date: date) -> bool:
    """
    Send an email reminder for a book that is due soon.
    
    Args:
        user_email: User's email address
        user_name: User's full name
        book_title: Title of the borrowed book
        due_date: Due date of the book
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not user_email:
        logger.warning(f"No email address for user {user_name}")
        return False
    
    try:
        days_until_due = (due_date - date.today()).days
        
        subject = "ShelfSmart - Book Due Soon Reminder"
        message = (
            f"Hello {user_name},\n\n"
            f"This is a friendly reminder that the book \"{book_title}\" is due in {days_until_due} day(s).\n\n"
            f"Due Date: {due_date.strftime('%B %d, %Y')}\n\n"
            "Please return the book on or before the due date to avoid any penalties.\n\n"
            "Thank you for using ShelfSmart!\n\n"
            "Best regards,\n"
            "ShelfSmart Library Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user_email],
            fail_silently=False
        )
        
        logger.info(f"Due reminder sent to {user_email} for book '{book_title}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send due reminder to {user_email}: {str(e)}")
        return False


def send_overdue_notification_email(user_email: str, user_name: str, book_title: str, 
                                    due_date: date, days_overdue: int) -> bool:
    """
    Send an email notification for an overdue book.
    
    Args:
        user_email: User's email address
        user_name: User's full name
        book_title: Title of the borrowed book
        due_date: Due date of the book
        days_overdue: Number of days the book is overdue
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not user_email:
        logger.warning(f"No email address for user {user_name}")
        return False
    
    try:
        subject = "ShelfSmart - Overdue Book Notice"
        message = (
            f"Hello {user_name},\n\n"
            f"This is a notice that the book \"{book_title}\" is now overdue.\n\n"
            f"Due Date: {due_date.strftime('%B %d, %Y')}\n"
            f"Days Overdue: {days_overdue} day(s)\n\n"
            "Please return the book as soon as possible to avoid further penalties. "
            "Late returns may affect your borrowing privileges.\n\n"
            "If you have already returned the book, please disregard this message.\n\n"
            "Thank you for your prompt attention to this matter.\n\n"
            "Best regards,\n"
            "ShelfSmart Library Team"
        )
        
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[user_email],
            fail_silently=False
        )
        
        logger.info(f"Overdue notification sent to {user_email} for book '{book_title}'")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send overdue notification to {user_email}: {str(e)}")
        return False


def get_due_soon_records(days_threshold: int = 3) -> List[BorrowRecord]:
    """
    Get borrow records for books that are due soon (within the threshold).
    
    Args:
        days_threshold: Number of days to consider as "due soon" (default: 3)
    
    Returns:
        List of BorrowRecord objects that are due soon
    """
    today = date.today()
    threshold_date = today + timedelta(days=days_threshold)
    
    due_soon = BorrowRecord.objects.filter(
        is_returned=False,
        due_date__gte=today,
        due_date__lte=threshold_date
    ).select_related('book')
    
    return list(due_soon)


def get_overdue_records() -> List[BorrowRecord]:
    """
    Get borrow records for books that are overdue.
    
    Returns:
        List of BorrowRecord objects that are overdue
    """
    today = date.today()
    
    overdue = BorrowRecord.objects.filter(
        is_returned=False,
        due_date__lt=today
    ).select_related('book')
    
    return list(overdue)


def send_bulk_due_reminders(days_threshold: int = 3) -> Dict[str, Any]:
    """
    Send due reminders to all users with books due soon.
    
    Args:
        days_threshold: Number of days to consider as "due soon" (default: 3)
    
    Returns:
        Dictionary with success count, failure count, and details
    """
    due_soon_records = get_due_soon_records(days_threshold)
    
    success_count = 0
    failure_count = 0
    details = []
    
    for record in due_soon_records:
        try:
            user = User.objects.get(id=record.user_id)
            
            success = send_due_reminder_email(
                user_email=user.email,
                user_name=user.get_full_name(),
                book_title=record.book.title,
                due_date=record.due_date
            )
            
            if success:
                success_count += 1
                details.append({
                    'user': user.username,
                    'book': record.book.title,
                    'status': 'success'
                })
            else:
                failure_count += 1
                details.append({
                    'user': user.username,
                    'book': record.book.title,
                    'status': 'failed'
                })
                
        except User.DoesNotExist:
            failure_count += 1
            details.append({
                'user_id': record.user_id,
                'book': record.book.title,
                'status': 'user_not_found'
            })
            logger.warning(f"User {record.user_id} not found for borrow record")
        except Exception as e:
            failure_count += 1
            details.append({
                'user_id': record.user_id,
                'book': record.book.title,
                'status': 'error',
                'error': str(e)
            })
            logger.error(f"Error sending due reminder: {str(e)}")
    
    return {
        'total': len(due_soon_records),
        'success': success_count,
        'failure': failure_count,
        'details': details
    }


def send_bulk_overdue_notifications() -> Dict[str, Any]:
    """
    Send overdue notifications to all users with overdue books.
    
    Returns:
        Dictionary with success count, failure count, and details
    """
    overdue_records = get_overdue_records()
    today = date.today()
    
    success_count = 0
    failure_count = 0
    details = []
    
    for record in overdue_records:
        try:
            user = User.objects.get(id=record.user_id)
            days_overdue = (today - record.due_date).days
            
            success = send_overdue_notification_email(
                user_email=user.email,
                user_name=user.get_full_name(),
                book_title=record.book.title,
                due_date=record.due_date,
                days_overdue=days_overdue
            )
            
            if success:
                success_count += 1
                details.append({
                    'user': user.username,
                    'book': record.book.title,
                    'days_overdue': days_overdue,
                    'status': 'success'
                })
            else:
                failure_count += 1
                details.append({
                    'user': user.username,
                    'book': record.book.title,
                    'days_overdue': days_overdue,
                    'status': 'failed'
                })
                
        except User.DoesNotExist:
            failure_count += 1
            details.append({
                'user_id': record.user_id,
                'book': record.book.title,
                'status': 'user_not_found'
            })
            logger.warning(f"User {record.user_id} not found for borrow record")
        except Exception as e:
            failure_count += 1
            details.append({
                'user_id': record.user_id,
                'book': record.book.title,
                'status': 'error',
                'error': str(e)
            })
            logger.error(f"Error sending overdue notification: {str(e)}")
    
    return {
        'total': len(overdue_records),
        'success': success_count,
        'failure': failure_count,
        'details': details
    }
