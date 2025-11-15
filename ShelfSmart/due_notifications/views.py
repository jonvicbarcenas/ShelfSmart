from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse, HttpRequest, HttpResponse
from user_auth.decorators import admin_required
import logging

from .email_utils import send_bulk_due_reminders, send_bulk_overdue_notifications

logger = logging.getLogger(__name__)


@admin_required
def send_due_reminders(request: HttpRequest) -> HttpResponse:
    """
    Admin action to send due reminders to users with books due soon.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("/admin-panel/catalog/admin/")
    
    try:
        # Get days threshold from POST data, default to 3 days
        days_threshold = int(request.POST.get("days_threshold", 3))
        
        # Send bulk due reminders
        result = send_bulk_due_reminders(days_threshold)
        
        # Prepare success message
        if result['success'] > 0:
            messages.success(
                request,
                f"Successfully sent {result['success']} due reminder(s) out of {result['total']} eligible borrower(s)."
            )
        
        # Add warning if there were failures
        if result['failure'] > 0:
            messages.warning(
                request,
                f"Failed to send {result['failure']} reminder(s). Check logs for details."
            )
        
        # If no eligible borrowers
        if result['total'] == 0:
            messages.info(request, "No books are due soon. No reminders sent.")
        
        logger.info(
            f"Admin {request.user.username} sent due reminders: "
            f"{result['success']} success, {result['failure']} failed"
        )
        
        # Check if it's an AJAX request
        if _is_ajax(request):
            return JsonResponse({
                'success': True,
                'result': result,
                'message': f"Sent {result['success']} out of {result['total']} reminders."
            })
        
    except ValueError:
        messages.error(request, "Invalid days threshold value.")
        logger.error(f"Invalid days threshold in send_due_reminders")
    except Exception as e:
        messages.error(request, f"Error sending reminders: {str(e)}")
        logger.error(f"Error in send_due_reminders: {str(e)}")
        
        if _is_ajax(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return redirect("/admin-panel/catalog/admin/")


@admin_required
def send_overdue_notifications(request: HttpRequest) -> HttpResponse:
    """
    Admin action to send overdue notifications to users with overdue books.
    """
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect("/admin-panel/catalog/admin/")
    
    try:
        # Send bulk overdue notifications
        result = send_bulk_overdue_notifications()
        
        # Prepare success message
        if result['success'] > 0:
            messages.success(
                request,
                f"Successfully sent {result['success']} overdue notification(s) out of {result['total']} overdue borrower(s)."
            )
        
        # Add warning if there were failures
        if result['failure'] > 0:
            messages.warning(
                request,
                f"Failed to send {result['failure']} notification(s). Check logs for details."
            )
        
        # If no overdue borrowers
        if result['total'] == 0:
            messages.info(request, "No overdue books found. No notifications sent.")
        
        logger.info(
            f"Admin {request.user.username} sent overdue notifications: "
            f"{result['success']} success, {result['failure']} failed"
        )
        
        # Check if it's an AJAX request
        if _is_ajax(request):
            return JsonResponse({
                'success': True,
                'result': result,
                'message': f"Sent {result['success']} out of {result['total']} notifications."
            })
        
    except Exception as e:
        messages.error(request, f"Error sending notifications: {str(e)}")
        logger.error(f"Error in send_overdue_notifications: {str(e)}")
        
        if _is_ajax(request):
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return redirect("/admin-panel/catalog/admin/")


def _is_ajax(request: HttpRequest) -> bool:
    """Check if the request is an AJAX request."""
    return request.headers.get("x-requested-with") == "XMLHttpRequest"
