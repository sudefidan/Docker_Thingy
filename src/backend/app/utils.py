from django.shortcuts import get_object_or_404  # Import get_object_or_404
from .models import User, Notification, UserInterest, Community, CommunityLeader, Subscribed  # Import User and Notification

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

def create_notification_community_interest(community):
    """
    Finds users whose interests match the community category
    and sends them a notification.
    """
    if not community or not community.category:
        # If no community or no category, nothing to match against
        print(f"Skipping interest notification for community '{community.name if community else 'N/A'}' - no category provided.")
        return

    community_category = community.category.strip() # Use the category and trim whitespace

    if not community_category:
        # If category is empty after stripping, nothing to match
        print(f"Skipping interest notification for community '{community.name}' - category is empty.")
        return

    try:
        matching_user_interests = UserInterest.objects.filter(
            interest__icontains=community_category
        ).select_related('user')

        notified_users = set() # Keep track to avoid duplicate notifications per user

        for user_interest in matching_user_interests:
            user_to_notify = user_interest.user
            matched_interest = user_interest.interest # The specific interest that matched

            is_owner = (community.owner == user_to_notify)
            is_leader = CommunityLeader.objects.filter(community=community, user=user_to_notify).exists()
            is_subscribed = Subscribed.objects.filter(community=community, user=user_to_notify).exists()

            # Optional: Avoid notifying the community owner about their own community
            if is_owner or is_leader or is_subscribed:
                continue

            # Ensure we notify each user only once
            if user_to_notify.id in notified_users:
                continue

            # Construct the notification message - now referencing the category
            message = (f"Check out '{community.name}'! "
                       f"This community, categorized under '{community.category}', might align with your interests.")

            # Use the existing create_notification function
            if create_notification(user_to_notify.id, message):
                notified_users.add(user_to_notify.id)

        if notified_users:
            print(f"Sent category-match notifications for community '{community.name}' (category: '{community.category}') to {len(notified_users)} users.")
        else:
            print(f"No users found with interests matching category '{community.category}' for community '{community.name}'.")


    except Exception as e:
        # Log any unexpected errors during the notification process
        print(f"Error during notify_users_with_matching_interest for community {community.community_id} (category: {community_category}): {e}")
        import traceback
        print(traceback.format_exc()) # Log full traceback for debugging