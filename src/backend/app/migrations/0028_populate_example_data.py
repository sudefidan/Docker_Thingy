from django.db import migrations
import random
from django.utils import timezone
import re
import os

def populate_data(apps, schema_editor):
    # Get models
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
    UserInterest = apps.get_model('app', 'UserInterest')
    Notification = apps.get_model('app', 'Notification')
    EventParticipant = apps.get_model('app', 'EventParticipant')
    SocialType = apps.get_model('app', 'SocialType')
    UserSocial = apps.get_model('app', 'UserSocial')
    PostImage = apps.get_model('app', 'PostImage')

    # Define path to images directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    IMAGES_DIR = os.path.join(BASE_DIR, 'app', 'migrations', 'images')

    # Define the directories for each image type
    PROFILE_PICS_DIR = os.path.join(IMAGES_DIR, 'profiles')
    COMMUNITY_PICS_DIR = os.path.join(IMAGES_DIR, 'communities')
    POST_PICS_DIR = os.path.join(IMAGES_DIR, 'posts')


    def get_specific_image(directory, filename):
        """Get a specific image by filename from the directory"""
        file_path = os.path.join(directory, filename)
        return read_image_file(file_path)

    # Helper function to read image file as binary
    def read_image_file(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None

    # Create social media types
    social_types = ["Instagram", "Twitter", "LinkedIn", "GitHub", "Facebook", "YouTube", "TikTok"]
    social_type_objects = {}

    for social in social_types:
        social_type, created = SocialType.objects.get_or_create(social_type=social)
        social_type_objects[social] = social_type
        if created:
            print(f"Created social type: {social}")
        else:
            print(f"Found existing social type: {social}")

    # Use categories from categories.json
    CATEGORIES = [
        "Football", "Basketball", "Baseball", "American Football", "Badminton", "Tennis",
        "Table Tennis", "Hockey", "Camping", "Fishing", "Hiking", "Running", "Yoga",
        "Pilates", "Weightlifting", "Archery", "Cheerleading", "Lacrosse", "Motorsports",
        "Netball", "Polo", "Gliding", "Climbing", "Golf", "Volleyball", "Rugby", "Cricket",
        "Boxing", "Wrestling", "Swimming", "Cycling", "Water Sports", "Winter Sports",
        "Extreme Sports", "Gymnastics", "Skating", "Art", "Drama", "Dance", "Anime",
        "Comics", "Movies", "Board Games", "Chess", "Economics", "Books", "Business",
        "Education", "Fashion", "Food", "Gaming", "Photography", "Politics", "Travel",
        "Theater", "History", "Geography", "Law", "Debate", "Volunteering", "Entrepreneurship",
        "Robotics", "Programming", "Pole Fitness", "Martial Arts", "Darts", "Film", "LGBTQ+",
        "Cooking", "K-Pop", "DnB", "Rap", "Rock", "Pop", "Classical Music", "Jazz",
        "Country Music", "Reggae", "Techno", "House", "R&B", "Electronic Music", "Hip Hop",
        "Music", "Philosophy", "Psychology", "Writing", "Gardening", "Model United Nations (MUN)",
        "Charity", "ESports", "Squash", "Bowling", "Animals", "Physics", "Artificial Intelligence",
        "Biomedical", "Chemistry", "Mathematics", "Astronomy", "Biology", "Engineering",
        "Medicine", "British Sign Language", "Formula One", "Hispanic", "Architecture",
        "Engineering", "Skateboarding", "Aerospace"
    ]

    # Helper function to extract mentions from content
    def extract_mentions(content):
        # Find all @username patterns
        mentions = re.findall(r'@(\w+)', content)
        return mentions

     # Create 10 Students with complete profiles
    students_data = [
        {
            'username': 'olivia_johnson',
            'email': 'olivia.johnson@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Olivia',
            'last_name': 'Johnson',
            'program': 'Computer Science',
            'uni_year': 3,
            'about': 'Tech enthusiast and software developer. Interested in AI and machine learning.',
            'address': '123 Campus Avenue, Apt 4B',
            'is_staff': True,
            'is_superuser': True,
            'interests': ['Programming', 'Artificial Intelligence', 'Gaming', 'Hiking'],
            'social_accounts': {
                'GitHub': 'olivia-dev',
                'LinkedIn': 'olivia-johnson-cs',
                'Twitter': 'olivia_codes'
            }
        },
        {
            'username': 'ethan_williams',
            'email': 'ethan.williams@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Ethan',
            'last_name': 'Williams',
            'program': 'Engineering',
            'uni_year': 2,
            'about': 'Mechanical engineering student with a passion for sustainable design.',
            'address': '456 University Drive',
            'interests': ['Robotics', 'Engineering', 'Football', 'Chess'],
            'social_accounts': {
                'LinkedIn': 'ethan-williams-eng',
                'Instagram': 'ethan.builds',
                'GitHub': 'ethan-williams'
            }
        },
        {
            'username': 'sophia_martinez',
            'email': 'sophia.martinez@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Sophia',
            'last_name': 'Martinez',
            'program': 'Business Administration',
            'uni_year': 4,
            'about': 'Aspiring entrepreneur with focus on fintech innovations.',
            'address': '789 College Street',
            'interests': ['Business', 'Entrepreneurship', 'Economics', 'Yoga'],
            'social_accounts': {
                'LinkedIn': 'sophia-martinez-business',
                'Twitter': 'sophia_fintech',
                'Instagram': 'sophia.entrepreneur'
            }
        },
        {
            'username': 'james_taylor',
            'email': 'james.taylor@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'James',
            'last_name': 'Taylor',
            'program': 'Environmental Science',
            'uni_year': 3,
            'about': 'Passionate about climate action and conservation biology.',
            'address': '234 Green Road',
            'interests': ['Biology', 'Hiking', 'Photography', 'Volunteering'],
            'social_accounts': {
                'Instagram': 'james.nature',
                'LinkedIn': 'james-taylor-enviro',
                'YouTube': 'JamesNatureChannel'
            }
        },
        {
            'username': 'ava_brown',
            'email': 'ava.brown@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Ava',
            'last_name': 'Brown',
            'program': 'Psychology',
            'uni_year': 2,
            'about': 'Studying cognitive psychology with interest in UX research.',
            'address': '567 Mind Avenue',
            'interests': ['Psychology', 'Art', 'Books', 'Running'],
            'social_accounts': {
                'LinkedIn': 'ava-brown-psych',
                'Instagram': 'ava.mindful',
                'Twitter': 'ava_psych'
            }
        },
        {

            'username': 'noah_garcia',
            'email': 'noah.garcia@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Noah',
            'last_name': 'Garcia',
            'program': 'Computer Engineering',
            'uni_year': 3,
            'about': 'Hardware enthusiast and IoT developer.',
            'address': '890 Tech Boulevard',
            'interests': ['Programming', 'Engineering', 'Cycling', 'Gaming'],
            'social_accounts': {
                'GitHub': 'noah-iot',
                'LinkedIn': 'noah-garcia-tech',
                'YouTube': 'NoahTechTips'
            }
        },
        {
            'username': 'emma_wilson',
            'email': 'emma.wilson@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'program': 'Literature',
            'uni_year': 4,
            'about': 'Creative writer focusing on contemporary fiction.',
            'address': '321 Literary Lane',
            'interests': ['Writing', 'Books', 'Poetry', 'Theater'],
            'social_accounts': {
                'Instagram': 'emma.writes',
                'Twitter': 'emma_novelist',
                'Facebook': 'EmmaWilsonAuthor'
            }
        },
        {
            'username': 'liam_patel',
            'email': 'liam.patel@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Liam',
            'last_name': 'Patel',
            'program': 'Mathematics',
            'uni_year': 2,
            'about': 'Math enthusiast with interest in cryptography and data analytics.',
            'address': '123 Number Street',
            'interests': ['Mathematics', 'Chess', 'Swimming', 'Board Games'],
            'social_accounts': {
                'GitHub': 'liam-math',
                'LinkedIn': 'liam-patel-math',
                'Twitter': 'liam_numbers'
            }
        },
        {
            'username': 'chloe_zhang',
            'email': 'chloe.zhang@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Chloe',
            'last_name': 'Zhang',
            'program': 'Computer Graphics',
            'uni_year': 3,
            'about': 'Digital artist and game developer specializing in 3D modeling.',
            'address': '456 Digital Avenue',
            'interests': ['Art', 'Gaming', 'Digital Art', 'Animation'],
            'social_accounts': {
                'Instagram': 'chloe.creates',
                'YouTube': 'ChloeDesigns',
                'TikTok': 'chloe_arts'
            }
        },
        {
            'username': 'benjamin_ahmed',
            'email': 'benjamin.ahmed@live.uwe.ac.uk',
            'password': 'SecurePass123',
            'first_name': 'Benjamin',
            'last_name': 'Ahmed',
            'program': 'Data Science',
            'uni_year': 4,
            'about': 'Working on machine learning applications for healthcare.',
            'address': '789 Algorithm Road',
            'interests': ['Artificial Intelligence', 'Mathematics', 'Medicine', 'Running'],
            'social_accounts': {
                'GitHub': 'benjamin-ai',
                'LinkedIn': 'benjamin-ahmed-ai',
                'Twitter': 'ben_datascience'
            }
        }
    ]

    users_data = []
    username_to_user = {}  # Dictionary for quick username lookups

    for student in students_data:
        interests = student.pop('interests', [])
        social_accounts = student.pop('social_accounts', {})
        username = student['username']

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(**student)
            print(f"Created user: {student['first_name']} {student['last_name']}")
        else:
            user = User.objects.get(username=username)
            print(f"Found existing user: {student['first_name']} {student['last_name']}")

        users_data.append(user)
        username_to_user[username] = user

        # Add interests for each user (only from valid categories)
        for interest in interests:
            if interest in CATEGORIES:
                UserInterest.objects.get_or_create(user=user, interest=interest)

        # Add social media accounts for each user
        for platform, username in social_accounts.items():
            if platform in social_type_objects:
                user_social, created = UserSocial.objects.get_or_create(
                    user=user,
                    social_type=social_type_objects[platform],
                    defaults={'social_username': username}
                )
                if created:
                    print(f"Added {platform} account '{username}' for {user.first_name}")
                else:
                    # Update username if it exists but is different
                    if user_social.social_username != username:
                        user_social.social_username = username
                        user_social.save()
                        print(f"Updated {platform} account to '{username}' for {user.first_name}")

    # Add profile pictures to specific users
    profile_mappings = {
        'sophia_martinez': 'sophia_martinez.jpg',
        'emma_wilson': 'emma_wilson.jpg',
        'ethan_williams': 'ethan_williams.jpg',
        'james_taylor': 'james_taylor.jpg',
        'liam_patel': 'liam_patel.jpg'
    }

    for username, image_filename in profile_mappings.items():
        if username in username_to_user:
            user = username_to_user[username]
            user.profile_picture = get_specific_image(PROFILE_PICS_DIR, image_filename)
            user.save()
            print(f"Added profile picture for {user.first_name} {user.last_name}")


    # Reference users by variable names for clarity
    user1 = users_data[0]  # Olivia
    user2 = users_data[1]  # Ethan
    user3 = users_data[2]  # Sophia
    user4 = users_data[3]  # James
    user5 = users_data[4]  # Ava
    user6 = users_data[5]  # Noah
    user7 = users_data[6]  # Emma
    user8 = users_data[7]  # Liam
    user9 = users_data[8]  # Chloe
    user10 = users_data[9]  # Benjamin

    # Create event types if not exist
    event_type_virtual, _ = EventType.objects.get_or_create(name='virtual')
    event_type_in_person, _ = EventType.objects.get_or_create(name='in-person')

    # Create Communities (3) with valid categories from the JSON file
    communities_data = [
        {
            'name': 'Tech Innovators Hub',
            'description': 'A community for students passionate about technology innovation, coding projects, and the future of tech.',
            'category': 'Programming',
            'owner': user1,  # Olivia Johnson
            'is_active': True
        },
        {
            'name': 'Environmental Action Group',
            'description': 'Focused on environmental sustainability projects, renewable energy, and campus greening initiatives.',
            'category': 'Biology',
            'owner': user4,  # James Taylor
            'is_active': True
        },
        {
            'name': 'Business Leaders Network',
            'description': 'For budding entrepreneurs to network, share ideas, and collaborate on business ventures.',
            'category': 'Entrepreneurship',
            'owner': user3,  # Sophia Martinez
            'is_active': True
        }
    ]

    communities = []
    for comm_data in communities_data:
        community, created = Community.objects.get_or_create(
            name=comm_data['name'],
            defaults=comm_data
        )

        if not created and not community.is_active:
            community.is_active = True
            community.save(update_fields=['is_active'])
            print(f"Updated existing community '{community.name}' to active.")
        elif created:
            print(f"Created community: {community.name}")
        else:
            print(f"Found existing community: {community.name}")

        communities.append(community)

        # Subscribe owner to the community
        Subscribed.objects.get_or_create(community=community, user=comm_data['owner'])

        # Generate notification for community creation
        if created:
            for user in users_data:
                if user != comm_data['owner']:
                    message = f"New community '{community.name}' created by {comm_data['owner'].first_name} {comm_data['owner'].last_name}"
                    Notification.objects.create(user=user, message=message)

    # Add community pictures to specific communities
    community_mappings = {
        'Tech Innovators Hub': 'tech.jpg',
        'Environmental Action Group': 'environment.jpg',
        'Business Leaders Network': 'business.jpg'
    }

    for community in communities:
        if community.name in community_mappings:
            community.community_picture = get_specific_image(COMMUNITY_PICS_DIR, community_mappings[community.name])
            community.save()
            print(f"Added picture for community: {community.name}")


    # Reference communities by name
    tech_community = communities[0]  # Tech Innovators Hub
    eco_community = communities[1]   # Environmental Action Group
    biz_community = communities[2]   # Business Leaders Network

    # Add members to communities - more distributed membership
    # Tech Innovators Hub members
    Subscribed.objects.get_or_create(community=tech_community, user=user2)  # Ethan
    Subscribed.objects.get_or_create(community=tech_community, user=user6)  # Noah
    Subscribed.objects.get_or_create(community=tech_community, user=user9)  # Chloe
    Subscribed.objects.get_or_create(community=tech_community, user=user10) # Benjamin

    # Notifications for community owner about new members
    for member in [user2, user6, user9, user10]:
        Notification.objects.create(
            user=tech_community.owner,
            message=f"{member.first_name} {member.last_name} joined your community '{tech_community.name}'"
        )

    # Environmental Action Group members
    Subscribed.objects.get_or_create(community=eco_community, user=user1)  # Olivia
    Subscribed.objects.get_or_create(community=eco_community, user=user5)  # Ava
    Subscribed.objects.get_or_create(community=eco_community, user=user2)  # Ethan

    # Notifications for community owner about new members
    for member in [user1, user5, user2]:
        Notification.objects.create(
            user=eco_community.owner,
            message=f"{member.first_name} {member.last_name} joined your community '{eco_community.name}'"
        )

    # Business Leaders Network members
    Subscribed.objects.get_or_create(community=biz_community, user=user1)  # Olivia
    Subscribed.objects.get_or_create(community=biz_community, user=user7)  # Emma
    Subscribed.objects.get_or_create(community=biz_community, user=user8)  # Liam

    # Notifications for community owner about new members
    for member in [user1, user7, user8]:
        Notification.objects.create(
            user=biz_community.owner,
            message=f"{member.first_name} {member.last_name} joined your community '{biz_community.name}'"
        )

    # Add community leaders
    CommunityLeader.objects.get_or_create(community=tech_community, user=user6)   # Noah as tech leader
    CommunityLeader.objects.get_or_create(community=tech_community, user=user10)  # Benjamin as tech leader
    CommunityLeader.objects.get_or_create(community=eco_community, user=user5)    # Ava as eco leader
    CommunityLeader.objects.get_or_create(community=biz_community, user=user7)    # Emma as business leader
    CommunityLeader.objects.get_or_create(community=biz_community, user=user8)    # Liam as business leader

    # Notification for new community leaders
    Notification.objects.create(user=user6, message=f"You've been made a leader of {tech_community.name}")
    Notification.objects.create(user=user10, message=f"You've been made a leader of {tech_community.name}")
    Notification.objects.create(user=user5, message=f"You've been made a leader of {eco_community.name}")
    Notification.objects.create(user=user7, message=f"You've been made a leader of {biz_community.name}")
    Notification.objects.create(user=user8, message=f"You've been made a leader of {biz_community.name}")

    # Create Events
    events_data = [
        {
            'title': 'AI Workshop: Machine Learning Fundamentals',
            'description': 'Learn the basics of machine learning with hands-on experience using Python and TensorFlow.',
            'date': timezone.now().date() + timezone.timedelta(days=10),
            'event_type': event_type_in_person,
            'community': tech_community,
            'location': 'Computer Science Building, Room 305',
            'max_capacity': 40,
            'materials': 'Laptop with Python installed, Google Colab account'
        },
        {
            'title': 'Campus Sustainability Forum',
            'description': 'Join us for an interactive discussion on improving sustainability initiatives on campus.',
            'date': timezone.now().date() + timezone.timedelta(days=15),
            'event_type': event_type_virtual,
            'community': eco_community,
            'location': 'Green Sciences Building Auditorium',
            'virtual_link': 'https://uwe-ac-uk.zoom.us/j/6789012345',
            'max_capacity': 75,
            'materials': 'Sustainability ideas to share'
        },
        {
            'title': 'Startup Pitch Competition',
            'description': 'Present your business ideas to a panel of judges and potential investors.',
            'date': timezone.now().date() + timezone.timedelta(days=21),
            'event_type': event_type_in_person,
            'community': biz_community,
            'location': 'Business School, Conference Hall B',
            'max_capacity': 50,
            'materials': 'Business proposal, presentation slides'
        },
        {
            'title': 'Hackathon 2025',
            'description': 'A 48-hour coding event to build innovative solutions for real-world problems.',
            'date': timezone.now().date() + timezone.timedelta(days=30),
            'event_type': event_type_in_person,
            'community': tech_community,
            'location': 'Tech Innovation Center',
            'max_capacity': 100,
            'materials': 'Laptop, charger, and enthusiasm!'
        }
    ]

    events = []
    for event_data in events_data:
        event, created = Event.objects.get_or_create(
            title=event_data['title'],
            community=event_data['community'],
            defaults=event_data
        )

        if created:
            print(f"Created event: {event.title}")

            # Create notifications for community members about new event
            community_subscribers = Subscribed.objects.filter(community=event_data['community'])
            for subscription in community_subscribers:
                Notification.objects.create(
                    user=subscription.user,
                    message=f"New event in {event_data['community'].name}: {event.title} on {event.date}"
                )
        else:
            print(f"Found existing event: {event.title}")

        events.append(event)

    # Add participants to events with more distribution across all students
    # AI Workshop participants
    for student in [user1, user2, user6, user9, user10]:  # Tech-oriented students
        EventParticipant.objects.get_or_create(event=events[0], user=student)
        if student != tech_community.owner:  # Don't notify owner about themselves
            Notification.objects.create(
                user=tech_community.owner,
                message=f"{student.first_name} is attending your event: {events[0].title}"
            )

    # Campus Sustainability Forum participants
    for student in [user1, user2, user4, user5]:  # Environment-interested students
        EventParticipant.objects.get_or_create(event=events[1], user=student)
        if student != eco_community.owner:  # Don't notify owner about themselves
            Notification.objects.create(
                user=eco_community.owner,
                message=f"{student.first_name} is attending your event: {events[1].title}"
            )

    # Startup Pitch Competition participants
    for student in [user1, user3, user7, user8]:  # Business-minded students
        EventParticipant.objects.get_or_create(event=events[2], user=student)
        if student != biz_community.owner:  # Don't notify owner about themselves
            Notification.objects.create(
                user=biz_community.owner,
                message=f"{student.first_name} is attending your event: {events[2].title}"
            )

    # Hackathon participants - broader participation
    for student in [user1, user2, user6, user8, user9, user10]:  # Tech and some others
        EventParticipant.objects.get_or_create(event=events[3], user=student)
        if student != tech_community.owner:  # Don't notify owner about themselves
            Notification.objects.create(
                user=tech_community.owner,
                message=f"{student.first_name} is attending your event: {events[3].title}"
            )

    # Create Posts with tags and hashtags
    posts_data = [
        # Community posts
        {
            'title': 'Welcome to Tech Innovators Hub!',
            'content': 'Excited to welcome everyone to our tech community! Looking forward to collaborating with @ethan_williams and @noah_garcia on upcoming projects. #Programming #Coding',
            'user': user1,  # Olivia
            'community': tech_community
        },
        {
            'title': 'AI Workshop Preparation',
            'content': 'For those attending the AI Workshop, @benjamin_ahmed and I have prepared some pre-workshop materials. Check your emails! #ArtificialIntelligence #Programming',
            'user': user10,  # Benjamin
            'community': tech_community
        },
        {
            'title': 'Join our Campus Clean-up Drive',
            'content': 'The Environmental Action Group is organising a campus-wide clean-up next week. Tag @ava_brown if you\'re interested in volunteering! #Volunteering #Biology',
            'user': user4,  # James
            'community': eco_community
        },
        {
            'title': 'Recycling Bins Update',
            'content': 'New recycling stations have been installed across campus. @ethan_williams helped design the new bin system. #Engineering #Volunteering',
            'user': user5,  # Ava
            'community': eco_community
        },
        {
            'title': 'Entrepreneurship Workshop Series',
            'content': 'We\'re launching a monthly workshop series for aspiring entrepreneurs. @emma_wilson will be hosting the first session on business plan development. #Business #Entrepreneurship',
            'user': user3,  # Sophia
            'community': biz_community
        },
        {
            'title': 'Networking Event Next Month',
            'content': 'Excited to announce we\'ll have representatives from local startups at our next networking event! @liam_patel is coordinating. #Business #Economics',
            'user': user7,  # Emma
            'community': biz_community
        },
        # General posts (visible to everyone)
        {
            'title': 'Study Group for Finals',
            'content': 'I\'m organising a study group for upcoming finals. Anyone interested? @noah_garcia @ava_brown #Education #Mathematics',
            'user': user2  # Ethan
        },
        {
            'title': 'Career Fair Announcement',
            'content': 'Don\'t miss the annual career fair next month! Great opportunity to connect with potential employers. @sophia_martinez shared that several tech companies will be recruiting. #Business #Engineering',
            'user': user1  # Olivia
        },
        {
            'title': 'New Campus Food Options',
            'content': 'Has anyone tried the new café in the Student Union? @james_taylor mentioned their great vegan options! #Food #Photography',
            'user': user5  # Ava
        },
        {
            'title': 'Book Exchange Program',
            'content': 'I\'m starting a book exchange program for literature students. @emma_wilson is helping coordinate. Comment if you\'re interested! #Books #Education',
            'user': user7  # Emma
        },
        {
            'title': '3D Modeling Workshop Interest',
            'content': 'Thinking of organising a weekend workshop on 3D modeling basics. Tag @benjamin_ahmed if you\'d be interested! #Art #Gaming',
            'user': user9  # Chloe
        },
        {
            'title': 'Math Tutoring Available',
            'content': 'Offering math tutoring for Calculus and Linear Algebra. DM me if interested!',
            'user': user8  # Liam
        }
    ]

    for post_data in posts_data:
        post, created = Post.objects.get_or_create(
            title=post_data['title'],
            user=post_data['user'],
            defaults=post_data
        )

        if created:
            print(f"Created post: {post.title}")

            # Create notifications for mentions/tags in posts
            mentions = extract_mentions(post_data['content'])
            for username in mentions:
                if username in username_to_user:
                    tagged_user = username_to_user[username]
                    message = f"{post_data['user'].first_name} {post_data['user'].last_name} mentioned you in post: '{post.title}'"
                    Notification.objects.create(user=tagged_user, message=message)
                    print(f"Created tag notification for {username}: {message}")

            # Notifications for community posts
            if 'community' in post_data and post_data['community']:
                subscribers = Subscribed.objects.filter(community=post_data['community'])
                for subscription in subscribers:
                    if subscription.user != post_data['user']:  # Don't notify the post author
                        message = f"New post in {post_data['community'].name}: '{post.title}'"
                        Notification.objects.create(user=subscription.user, message=message)
        else:
            print(f"Found existing post: {post.title}")

        # Add comments to selected posts
        if post.title == 'Welcome to Tech Innovators Hub!':
            comment_content = 'Excited to be part of this community! Looking forward to the upcoming AI workshop. #Programming'
            comment1, c1_created = Comment.objects.get_or_create(
                post=post,
                user=user2,  # Ethan
                comment=comment_content
            )
            if c1_created and post.user != user2:
                # Notify post author about the comment
                Notification.objects.create(
                    user=post.user,
                    message=f"{user2.first_name} commented on your post: '{post.title}'"
                )

            comment_content2 = 'Thanks for the mention @ethan_williams! Can\'t wait to collaborate on some exciting projects.'
            comment2, c2_created = Comment.objects.get_or_create(
                post=post,
                user=user6,  # Noah
                comment=comment_content2
            )
            if c2_created:
                # Notify post author about the comment
                if post.user != user6:
                    Notification.objects.create(
                        user=post.user,
                        message=f"{user6.first_name} commented on your post: '{post.title}'"
                    )

                # Notify about the mention in comment
                mentions = extract_mentions(comment_content2)
                for username in mentions:
                    if username in username_to_user:
                        tagged_user = username_to_user[username]
                        # Don't notify if commenter is tagging themselves
                        if tagged_user != user6:
                            message = f"{user6.first_name} mentioned you in a comment on '{post.title}'"
                            Notification.objects.create(user=tagged_user, message=message)
                            print(f"Created tag notification in comment for {username}: {message}")

            # Add a third comment from Benjamin
            comment_content3 = 'Great initiative! I\'m particularly interested in the AI aspects of our community projects. #ArtificialIntelligence'
            comment3, c3_created = Comment.objects.get_or_create(
                post=post,
                user=user10,  # Benjamin
                comment=comment_content3
            )
            if c3_created and post.user != user10:
                Notification.objects.create(
                    user=post.user,
                    message=f"{user10.first_name} commented on your post: '{post.title}'"
                )

        elif post.title == 'Join our Campus Clean-up Drive':
            comment_content = 'Count me in! I\'ll bring some friends from Psychology department too. #Volunteering'
            comment, c_created = Comment.objects.get_or_create(
                post=post,
                user=user5,  # Ava
                comment=comment_content
            )
            if c_created and post.user != user5:
                Notification.objects.create(
                    user=post.user,
                    message=f"{user5.first_name} commented on your post: '{post.title}'"
                )

            comment2_content = 'Great initiative @james_taylor! What time should we meet?'
            comment2, c2_created = Comment.objects.get_or_create(
                post=post,
                user=user1,  # Olivia
                comment=comment2_content
            )
            if c2_created:
                # Notify post author about the comment if not self
                if post.user != user1:
                    Notification.objects.create(
                        user=post.user,
                        message=f"{user1.first_name} commented on your post: '{post.title}'"
                    )

                # Notify about mention
                mentions = extract_mentions(comment2_content)
                for username in mentions:
                    if username in username_to_user:
                        tagged_user = username_to_user[username]
                        if tagged_user != user1:  # Don't notify self
                            message = f"{user1.first_name} mentioned you in a comment on '{post.title}'"
                            Notification.objects.create(user=tagged_user, message=message)

            # Add a third comment from Ethan
            comment3_content = 'The Engineering department would like to help too. We can bring some equipment if needed. @james_taylor let me know what would be useful. #Engineering'
            comment3, c3_created = Comment.objects.get_or_create(
                post=post,
                user=user2,  # Ethan
                comment=comment3_content
            )
            if c3_created:
                if post.user != user2:
                    Notification.objects.create(
                        user=post.user,
                        message=f"{user2.first_name} commented on your post: '{post.title}'"
                    )

                # Notify about mention
                mentions = extract_mentions(comment3_content)
                for username in mentions:
                    if username in username_to_user:
                        tagged_user = username_to_user[username]
                        if tagged_user != user2:  # Don't notify self
                            message = f"{user2.first_name} mentioned you in a comment on '{post.title}'"
                            Notification.objects.create(user=tagged_user, message=message)

        elif post.title == 'Study Group for Finals':
            comment_content = 'I\'m interested! The CS library has good study rooms we could reserve.'
            comment, c_created = Comment.objects.get_or_create(
                post=post,
                user=user6,  # Noah
                comment=comment_content
            )
            if c_created and post.user != user6:
                Notification.objects.create(
                    user=post.user,
                    message=f"{user6.first_name} commented on your post: '{post.title}'"
                )

            comment2_content = 'Thanks for tagging me @ethan_williams! I\'ll join for the psychology study sessions. #Psychology'
            comment2, c2_created = Comment.objects.get_or_create(
                post=post,
                user=user5,  # Ava
                comment=comment2_content
            )
            if c2_created:
                if post.user != user5:
                    Notification.objects.create(
                        user=post.user,
                        message=f"{user5.first_name} commented on your post: '{post.title}'"
                    )

                # Notify about mention
                mentions = extract_mentions(comment2_content)
                for username in mentions:
                    if username in username_to_user:
                        tagged_user = username_to_user[username]
                        if tagged_user != user5:  # Don't notify self
                            message = f"{user5.first_name} mentioned you in a comment on '{post.title}'"
                            Notification.objects.create(user=tagged_user, message=message)

            comment3_content = 'I can help with the Computer Science subjects if anyone needs assistance! #Programming'
            comment3, c3_created = Comment.objects.get_or_create(
                post=post,
                user=user1,  # Olivia
                comment=comment3_content
            )
            if c3_created and post.user != user1:
                Notification.objects.create(
                    user=post.user,
                    message=f"{user1.first_name} commented on your post: '{post.title}'"
                )

            # Add a fourth comment from Benjamin
            comment4_content = 'I\'d be happy to help with AI and machine learning topics. @noah_garcia shall we coordinate? #ArtificialIntelligence'
            comment4, c4_created = Comment.objects.get_or_create(
                post=post,
                user=user10,  # Benjamin
                comment=comment4_content
            )
            if c4_created:
                if post.user != user10:
                    Notification.objects.create(
                        user=post.user,
                        message=f"{user10.first_name} commented on your post: '{post.title}'"
                    )

                # Notify about mention
                mentions = extract_mentions(comment4_content)
                for username in mentions:
                    if username in username_to_user:
                        tagged_user = username_to_user[username]
                        if tagged_user != user10:  # Don't notify self
                            message = f"{user10.first_name} mentioned you in a comment on '{post.title}'"
                            Notification.objects.create(user=tagged_user, message=message)

        # Add likes to posts - each user likes multiple posts
        for i, user in enumerate(users_data):
            # Skip the post author to avoid self-likes
            if user != post.user:
                # Like posts based on a pattern to ensure good distribution
                if (i + int(post.post_id)) % 2 != 0:  # Changed from %3 to %2 to increase like density
                    like, like_created = PostLikes.objects.get_or_create(post=post, user=user)
                    print(f"User {user.username} liked post '{post.title}'")

                    # Create notification for post like
                    if like_created:
                        Notification.objects.create(
                            user=post.user,
                            message=f"{user.first_name} {user.last_name} liked your post: '{post.title}'"
                        )

    # Add images to specific posts
    post_mappings = {
        '3D Modeling Workshop Interest': '3dmodelling.jpg',
        'Recycling Bins Update': 'recyclingbins.jpg'
    }

    for post_title, image_filename in post_mappings.items():
        try:
            post = Post.objects.get(title=post_title)
            image_data = get_specific_image(POST_PICS_DIR, image_filename)

            if image_data:
                PostImage.objects.create(
                    post=post,
                    image=image_data
                )
                print(f"Added image to post: {post.title}")
        except Post.DoesNotExist:
            print(f"Post '{post_title}' not found")
        except Exception as e:
            print(f"Error adding image to post '{post_title}': {e}")


    # Create connections between users (follows)
    # Each user follows several others for better network connectivity
    for i, follower in enumerate(users_data):
        # Each user follows 5-8 other users (increased from previous 3-5)
        num_to_follow = random.randint(5, 8)
        potential_following = [u for u in users_data if u != follower]
        users_to_follow = random.sample(potential_following, min(num_to_follow, len(potential_following)))

        for following in users_to_follow:
            connection, conn_created = Connection.objects.get_or_create(follower=follower, following=following)
            print(f"User {follower.username} now follows {following.username}")

            # Create notification for new follower
            if conn_created:
                Notification.objects.create(
                    user=following,
                    message=f"{follower.first_name} {follower.last_name} started following you"
                )

    print("Data population complete with 10 students, communities, events, posts, and notifications.")


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0027_connection'),
    ]

    operations = [
        migrations.RunPython(populate_data),
    ]