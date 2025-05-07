from django.contrib import admin
from .models import (
    Community, Event, EventType, Post, Subscribed, User, SocialType,
    UserSocial, CommunityLeader, EventParticipant, Notification, Comment,
    UserInterest, PostImage, PostLikes
)
from .utils import create_notification_community_interest # Import the utility function

# User model (custom user model)
admin.site.register(User)

# Community related models
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'category', 'is_active', 'community_id')
    list_filter = ('is_active', 'category', 'owner')
    search_fields = ('name', 'description', 'category')
    actions = ['make_active_and_notify', 'make_inactive']

    def save_model(self, request, obj, form, change):
        """
        Override save_model to trigger notifications when a community is activated.
        """
        old_is_active = None
        if change: # If it's an update
            try:
                old_community = Community.objects.get(pk=obj.pk)
                old_is_active = old_community.is_active
            except Community.DoesNotExist:
                pass # Should not happen for an update if obj.pk exists

        super().save_model(request, obj, form, change) # Save the object

        # If an existing community was inactive and is now being activated
        if change and obj.is_active and old_is_active is False:
            create_notification_community_interest(obj)

    def make_active_and_notify(self, request, queryset):
        updated_count = 0
        for community in queryset.filter(is_active=False): # Only process currently inactive communities
            community.is_active = True
            community.save()
            create_notification_community_interest(community)
            updated_count += 1
        self.message_user(request, f"{updated_count} community/communities successfully activated and interest notifications sent.")
    make_active_and_notify.short_description = "Activate selected communities and notify by interest"

    def make_inactive(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(request, f"{updated_count} community/communities successfully deactivated.")
    make_inactive.short_description = "Deactivate selected communities"

admin.site.register(Community, CommunityAdmin) # Register Community with the custom admin class
admin.site.register(Subscribed)
admin.site.register(CommunityLeader)

# Event related models
admin.site.register(Event)
admin.site.register(EventType)
admin.site.register(EventParticipant)

# Post related models
admin.site.register(Post)
admin.site.register(PostImage)
admin.site.register(PostLikes)
admin.site.register(Comment)

# User profile related models
admin.site.register(SocialType)
admin.site.register(UserSocial)
admin.site.register(UserInterest)

# Other models
admin.site.register(Notification)