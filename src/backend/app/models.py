# python manage.py inspectdb
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Community(models.Model):
    community_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    owner = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
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
        managed = False
        db_table = 'Event'


class Eventtype(models.Model):
    event_type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'EventType'


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField()
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    community = models.ForeignKey(Community, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Post'


class Subscribed(models.Model):
    community = models.OneToOneField(Community, models.DO_NOTHING, primary_key=True)  # The composite primary key (community_id, user_id) found, that is not supported. The first column is selected.
    user = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Subscribed'
        unique_together = (('community', 'user'),)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    access_level = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'User'