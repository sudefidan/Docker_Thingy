# Generated by Django 4.2 on 2025-03-10 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_socialtype_usersocial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityLeader',
            fields=[
                ('community_leader_id', models.AutoField(primary_key=True, serialize=False)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.community')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'CommunityLeader',
                'unique_together': {('community', 'user')},
            },
        ),
    ]
