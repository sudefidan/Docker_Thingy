# Generated by Django 4.2 on 2025-05-02 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_community_community_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='materials',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
