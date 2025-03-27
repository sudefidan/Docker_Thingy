from django.shortcuts import get_object_or_404  # Import get_object_or_404
from .models import User, Notification  # Import User and Notification

def create_notification(user_id, message):
    """
    Creates a notification for a given user.
    """
    try:
        # Retrieve the user object using get_object_or_404 to handle non-existent users
        user = get_object_or_404(User, id=user_id)

        # Create the notification object
        Notification.objects.create(user=user, message=message)
        return True
    except Exception as e:
        print(f"Error creating notification: {e}")
        return False