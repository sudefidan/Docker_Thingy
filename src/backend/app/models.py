from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


class User(AbstractUser):
    access_level = models.IntegerField(default=1)
    about = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.BinaryField(blank=True, null=True)
    program = models.CharField(max_length=255, blank=True, null=True)
    uni_year = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    pending_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.username


class Community(models.Model):
    community_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    community_picture = models.BinaryField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'Community'

    def __str__(self):
        return self.name


class EventType(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    
    class Meta:
        db_table = 'EventType'

    def __str__(self):
        return self.name


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    virtual_link = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, blank=True, null=True)
    cancelled = models.BooleanField(default=False)
    max_capacity = models.IntegerField(blank=False, null=False, default=20)
    materials = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Event'

    def __str__(self):
        return self.title


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)  # Change DateField to DateTimeField
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    community = models.ForeignKey('Community', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'Post'

    def __str__(self):
        return self.title


class Subscribed(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Subscribed'
        unique_together = (('community', 'user'),)

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"


class SocialType(models.Model):
    social_type = models.CharField(max_length=255, unique=True, primary_key=True)

    class Meta:
        db_table = 'SocialType'

    def __str__(self):
        return self.social_type


class UserSocial(models.Model):
    user_social_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_type = models.ForeignKey(SocialType, on_delete=models.CASCADE)
    social_username = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'UserSocial'
        unique_together = ('user', 'social_type')

    def __str__(self):
        return f"{self.user.username} - {self.social_type.social_type}: {self.social_username}"


class CommunityLeader(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'CommunityLeader'
        unique_together = (('community', 'user'),)

    def __str__(self):
        return f"{self.user.username} - {self.community.name}"

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EventParticipant'
        unique_together = (('event', 'user'),)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    message = models.TextField(null=False)
    # Should auto add the current date when a record is created.
    timestamp = models.DateTimeField(auto_now_add=True, null=False) 

    class Meta:
        db_table = 'Notification'

# Comment already exists - just added unique constraint on user and post
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    comment = models.TextField(null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'Comment'
        # unique_together = (('post', 'user'),)

class UserInterest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    interest = models.TextField(null=False)

    class Meta:
        db_table ='UserInterest'
        
class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    image = models.BinaryField(blank=True, null=True)

    class Meta:
        db_table = 'PostImage'

class PostLikes(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = 'PostLikes'
        unique_together = (('post', 'user'),)


class Connection(models.Model):
    follower = models.ForeignKey(
        User,
        related_name='following_set',  # Users that this user is following
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        related_name='followers_set',  # Users that are following this user
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Connection'
        # Ensures that a user cannot follow another user more than once.
        unique_together = (('follower', 'following'),)

    def __str__(self):
        follower_username = getattr(self.follower, 'username', 'N/A') if self.follower_id else 'N/A'
        following_username = getattr(self.following, 'username', 'N/A') if self.following_id else 'N/A'
        return f"{follower_username} follows {following_username}"

    def clean(self):
        """
        Prevents self-following.
        """
        super().clean()
        if self.follower_id and self.following_id and self.follower_id == self.following_id:
            raise ValidationError("A user cannot follow themselves.")

    def save(self, *args, **kwargs):
         self.full_clean()
         super().save(*args, **kwargs)