# python manage.py inspectdb
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Community(models.Model):
    community_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'Community'


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    virtual_link = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    event_type = models.ForeignKey('Eventtype', models.DO_NOTHING, db_column='event_type', blank=True, null=True)
    community = models.ForeignKey(Community, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'Event'


class Eventtype(models.Model):
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'EventType'


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField()
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    community = models.ForeignKey(Community, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'Post'


class Subscribed(models.Model):
    community = models.OneToOneField(Community, models.DO_NOTHING, primary_key=True)  # The composite primary key (community_id, user_id) found, that is not supported. The first column is selected.
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        db_table = 'Subscribed'
        unique_together = (('community', 'user'),)

# Inherit from base Django user and add access_level
class User(AbstractUser):
    access_level = models.IntegerField(default=1)
    about = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.BinaryField(
        blank=True, 
        null=True, 
    )

class SocialType(models.Model):
    social_type = models.CharField(max_length=255, unique=True, primary_key=True)

    def __str__(self):
        return self.social_type
    
    class Meta:
      db_table = 'SocialType'

    def __str__(self):
        return self.username

class UserSocial(models.Model):
    user_social_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    social_type = models.ForeignKey(SocialType, on_delete=models.CASCADE)
    social_username = models.CharField(max_length=255, null=False)

    class Meta:
        db_table = 'UserSocial'
        unique_together = ('user', 'social_type') # A user can have only one social link of each type
    
    def __str__(self):
        return f"{self.user.username} - {self.social_type.name}: {self.name}"

class CommunityLeader(models.Model):
    community_leader_id = models.AutoField(primary_key=True)
    community = models.ForeignKey(Community, on_delete=models.CASCADE) # Django will append _id in DB
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Django will append _id in DB

    class Meta:
        db_table = 'CommunityLeader'
        unique_together = ('community', 'user') # A user can only be a leader of one community once