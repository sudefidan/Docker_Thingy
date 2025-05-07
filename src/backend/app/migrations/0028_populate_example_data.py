from django.db import migrations
import random # For generating random relationships
from django.utils import timezone # For setting dates if needed

def populate_data(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import models, it might be a newer version than this migration expects.
    User = apps.get_model('app', 'User')
    Community = apps.get_model('app', 'Community')
    EventType = apps.get_model('app', 'EventType')
    Event = apps.get_model('app', 'Event')
    Post = apps.get_model('app', 'Post')
    Subscribed = apps.get_model('app', 'Subscribed')
    Comment = apps.get_model('app', 'Comment')
    PostLikes = apps.get_model('app', 'PostLikes')
    CommunityLeader = apps.get_model('app', 'CommunityLeader')
    Connection = apps.get_model('app', 'Connection')

    # Create Users
    users_data = []
    for i in range(1, 11): # Create 10 users
        username = f'example_user{i}' # Changed from 'user{i}' for clarity
        email = f'example_user{i}@example.com'
        # Check if user already exists to make migration rerunnable (optional, good practice)
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=f'Password123', # Use strong, unique passwords in a real scenario
                first_name=f'Example',
                last_name=f'User{i}',
                is_staff= (i==1), # Make the first user a staff user for example
                is_superuser= (i==1), # Make the first user a superuser
                is_active=True,
                access_level=1,
                program="Computer Science",
                uni_year=3,
                address="123 Example St, City, Country",
            )
            users_data.append(user)
        else:
            users_data.append(User.objects.get(username=username))

    if not users_data:
        print("No users created or found, stopping data population.")
        return

    user1 = users_data[0]
    user2 = users_data[1] if len(users_data) > 1 else user1

    # Create EventTypes
    event_type_virtual, _ = EventType.objects.get_or_create(name='virtual')
    event_type_in_person, _ = EventType.objects.get_or_create(name='in-person')

    # Create Communities
    community1_data = {
        'name': 'Tech Innovators Club',
        'description': 'A club for students passionate about technology and innovation.',
        'category': 'Technology',
        'owner': user1,
        'is_active': True
    }
    community1, created1 = Community.objects.get_or_create(
        name=community1_data['name'], # Lookup by name
        defaults=community1_data      # Pass all data as defaults
    )

    if not created1 and not community1.is_active: # If found and was not active
        community1.is_active = True
        community1.save(update_fields=['is_active'])
        print(f"Updated existing community '{community1.name}' to active.")
    elif created1:
        print(f"Created community: {community1.name} (Active: {community1.is_active})")
    else: # Found and already active
        print(f"Found existing community: {community1.name} (Active: {community1.is_active})")
    # Subscribe owner and another user
    Subscribed.objects.get_or_create(community=community1, user=user1)
    Subscribed.objects.get_or_create(community=community1, user=user2)


    community2_data = {
        'name': 'Sustainable Futures Group',
        'description': 'Focused on environmental sustainability projects and discussions.',
        'category': 'Environment',
        'owner': user2,
        'is_active': True
    }
    community2, created2 = Community.objects.get_or_create(
        name=community2_data['name'], # Lookup by name
        defaults=community2_data      # Pass all data as defaults
    )

    if not created2 and not community2.is_active: # If found and was not active
        community2.is_active = True
        community2.save(update_fields=['is_active'])
        print(f"Updated existing community '{community2.name}' to active.")
    elif created2:
        print(f"Created community: {community2.name} (Active: {community2.is_active})")
    else: # Found and already active
        print(f"Found existing community: {community2.name} (Active: {community2.is_active})")
    Subscribed.objects.get_or_create(community=community2, user=user2)


    # Create Events
    event_date = timezone.now().date() + timezone.timedelta(days=7)

    event1_data = {
        'title': 'Intro to Django Workshop',
        'description': 'Learn the basics of Django web framework.',
        'date': event_date,
        'event_type': event_type_in_person,
        'community': community1,
        'location': 'Room 404, CS Building',
        'max_capacity': 50,
        'materials': 'Laptop with Python installed'
    }
    # Check if event with this title for this community already exists
    if not Event.objects.filter(title=event1_data['title'], community=community1).exists():
        Event.objects.create(**event1_data)
        print(f"Created event: {event1_data['title']}")


    event2_data = {
        'title': 'Guest Lecture: AI in Healthcare',
        'description': 'A talk by Dr. AI Expert on the future of AI in medicine.',
        'date': event_date + timezone.timedelta(days=14),
        'event_type': event_type_virtual,
        'community': community1,
        'virtual_link': 'https://example.zoom.us/j/1234567890',
        'max_capacity': 100
    }
    if not Event.objects.filter(title=event2_data['title'], community=community1).exists():
        Event.objects.create(**event2_data)
        print(f"Created event: {event2_data['title']}")

    # Create Posts
    post1_data = {
        'title': 'Welcome to the Tech Club!',
        'content': 'Excited to have everyone here. Let\'s build amazing things!',
        'user': user1,
        'community': community1,
        # 'date' will be auto_now_add
    }
    # Check if post with this title by this user already exists
    post1, post1_created = Post.objects.get_or_create(title=post1_data['title'], user=user1, defaults=post1_data)
    if post1_created:
        print(f"Created post: {post1_data['title']}")
    
    post2_data = {
        'title': 'First General Post',
        'content': 'This is a post visible to everyone, not tied to a specific community.',
        'user': user2,
        # 'community': None, # For a general post
    }
    if not Post.objects.filter(title=post2_data['title'], user=user2).exists():
        post2, post2_created = Post.objects.get_or_create(title=post2_data['title'], user=user2, defaults=post2_data)
        if post2_created:
            print(f"Created post: {post2_data['title']}")
    else:
        post2 = Post.objects.get(title=post2_data['title'], user=user2)

    # Create Comments
    if post1: # Ensure post1 was created or fetched
        comment1_data = {
            'post': post1,
            'user': user2, # Another user comments
            'comment': f'Great post, @{user1.username}! Really excited about this. #TechInnovation'
        }
        # Check if this specific comment by this user on this post already exists
        if not Comment.objects.filter(post=post1, user=user2, comment=comment1_data['comment']).exists():
            Comment.objects.create(**comment1_data)
            print(f"Created comment on '{post1.title}' by {user2.username}")

    if post2: # Ensure post2 was created or fetched
        comment2_data = {
            'post': post2,
            'user': user1, # Another user comments
            'comment': 'Interesting general discussion point. What does everyone else think?'
        }
        if not Comment.objects.filter(post=post2, user=user1, comment=comment2_data['comment']).exists():
            Comment.objects.create(**comment2_data)
            print(f"Created comment on '{post2.title}' by {user1.username}")

    # Add more comments
    if post1 and len(users_data) > 2:
        user3 = users_data[2]
        comment3_data = {
            'post': post1,
            'user': user3,
            'comment': 'Looking forward to more updates from the Tech Innovators Club!'
        }
        if not Comment.objects.filter(post=post1, user=user3, comment=comment3_data['comment']).exists():
            Comment.objects.create(**comment3_data)
            print(f"Created comment on '{post1.title}' by {user3.username}")

    if post2 and len(users_data) > 3:
        user4 = users_data[3]
        comment4_data = {
            'post': post2,
            'user': user4,
            'comment': 'This is a great topic for discussion. #CommunityEngagement'
        }
        if not Comment.objects.filter(post=post2, user=user4, comment=comment4_data['comment']).exists():
            Comment.objects.create(**comment4_data)
            print(f"Created comment on '{post2.title}' by {user4.username}")

    # Create Post Likes
    if post1 and user2:
        PostLikes.objects.get_or_create(post=post1, user=user2)
        print(f"User {user2.username} liked post '{post1.title}'")
    if post2 and user1:
        PostLikes.objects.get_or_create(post=post2, user=user1)
        # Corrected print statement from previous version
        print(f"User {user1.username} liked post '{post2.title}'")

    # Add more likes to post1 (target: 6 total, already 1 from user2)
    if post1 and len(users_data) > 6: # Need at least user1 + 5 other users
        # Users from index 2 to 6 (5 users: user3, user4, user5, user6, user7)
        for i in range(2, 7): # users_data[2] to users_data[6]
            if i < len(users_data): # Ensure user exists
                liker = users_data[i]
                if liker != post1.user: # Don't let the post owner like their own post again if already handled
                    PostLikes.objects.get_or_create(post=post1, user=liker)
                    print(f"User {liker.username} liked post '{post1.title}'")

    # Add more likes to post2 (target: 3 total, already 1 from user1)
    if post2 and len(users_data) > 3: # Need at least user2 + 2 other users
        # Users from index 2 to 3 (2 users: user3, user4)
        for i in range(2, 4): # users_data[2] to users_data[3]
            if i < len(users_data): # Ensure user exists
                liker = users_data[i]
                if liker != post2.user:
                    PostLikes.objects.get_or_create(post=post2, user=liker)
                    print(f"User {liker.username} liked post '{post2.title}'")

    # Create Community Leaders

    if community1 and len(users_data) > 1: # Check if user2 (users_data[1]) exists
        leader_for_community1 = users_data[1] # This is 'example_user2'
        CommunityLeader.objects.get_or_create(community=community1, user=leader_for_community1)
        print(f"Made {leader_for_community1.username} a leader of '{community1.name}'")

    if community2 and len(users_data) > 2: # Check if user3 (users_data[2]) exists
        leader_for_community2 = users_data[2] # This is 'example_user3'
        CommunityLeader.objects.get_or_create(community=community2, user=leader_for_community2)
        print(f"Made {leader_for_community2.username} a leader of '{community2.name}'")


    # Create Random Connections (Follows)
    if len(users_data) > 1: # Only proceed if there's more than one user
        for user_obj in users_data:
            # Each user will follow a random number of other users (e.g., 0 to 3)
            
            num_to_follow = random.randint(1, min(10, len(users_data) - 1)) # Cannot follow more users than exist (excluding self)
            
            # Get a list of users *other* than the current user_obj
            potential_to_follow = [u for u in users_data if u.id != user_obj.id]
            
            if not potential_to_follow: # Should not happen if len(users_data) > 1
                continue

            users_to_actually_follow = random.sample(potential_to_follow, min(num_to_follow, len(potential_to_follow)))
            
            for followed_user in users_to_actually_follow:
                Connection.objects.get_or_create(follower=user_obj, following=followed_user)
                print(f"User {user_obj.username} now randomly follows {followed_user.username}")

    print("Example data population complete.")


class Migration(migrations.Migration):

    # This migration should run after all the models in 'app' have been created.
    dependencies = [
        ('app', '0027_connection'),
    ]

    operations = [
        migrations.RunPython(populate_data),
    ]
