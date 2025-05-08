# UniHub

UniHub is a university community platform designed to connect students, facilitate event organisation, and promote campus engagement through interest-based communities and events.

## Getting Started

**IMPORTANT**: In order to run, please open the root folder with a command line tool and with Docker running, run the command "Docker Compose Up --Build" and it should build and run the project - with the front-end accessible at http://localhost:5173/. The admin panel can be accessed at http://localhost:8000/admin. Further instructions below.

### Access URLs

- **GitHub Repo**: [https://github.com/sudefidan/Docker_Thingy.git](https://github.com/sudefidan/Docker_Thingy.git)
- **Frontend Application**: [http://localhost:5173/](http://localhost:5173/)
- **Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)

### User Accounts

The system includes ten student accounts with complete profiles (including program details, interests, and social media accounts):

| Username        | Email                          | Password      | Role                      |
| --------------- | ------------------------------ | ------------- | ------------------------- |
| olivia_johnson  | olivia.johnson@live.uwe.ac.uk  | SecurePass123 | Admin (Staff & Superuser) |
| ethan_williams  | ethan.williams@live.uwe.ac.uk  | SecurePass123 | Student                   |
| sophia_martinez | sophia.martinez@live.uwe.ac.uk | SecurePass123 | Student                   |
| james_taylor    | james.taylor@live.uwe.ac.uk    | SecurePass123 | Student                   |
| ava_brown       | ava.brown@live.uwe.ac.uk       | SecurePass123 | Student                   |
| noah_garcia     | noah.garcia@live.uwe.ac.uk     | SecurePass123 | Student                   |
| emma_wilson     | emma.wilson@live.uwe.ac.uk     | SecurePass123 | Student                   |
| liam_patel      | liam.patel@live.uwe.ac.uk      | SecurePass123 | Student                   |
| chloe_zhang     | chloe.zhang@live.uwe.ac.uk     | SecurePass123 | Student                   |
| benjamin_ahmed  | benjamin.ahmed@live.uwe.ac.uk  | SecurePass123 | Student                   |

**Note**: For admin access, use Olivia's account as she has staff and superuser privileges.

## Platform Structure

### Communities

The platform includes three pre-configured communities:

1. **Tech Innovators Hub** - For technology enthusiasts and developers
2. **Environmental Action Group** - Focused on sustainability and environmental initiatives
3. **Business Leaders Network** - For entrepreneurship and business networking

Each community has designated leaders, members, and community-specific content.

### Events

Four pre-configured events are available:

1. **AI Workshop: Machine Learning Fundamentals** - In-person technical workshop
2. **Campus Sustainability Forum** - Virtual environmental discussion
3. **Startup Pitch Competition** - In-person business networking event
4. **Hackathon 2025** - Large-scale coding competition

Each event also has pre-registered attendees.

### Posts

There are some pre-defined interactive contents available: posts with comments, likes, #hashtags, @mentions and image attachments.

### Notifications

System comes with personalised alerts for various user interactions.

## Security Framework

UniHub implements a comprehensive security architecture with multiple protection layers:

### Access Control System

1. **User Access Tiers**

   - Regular users: Can create content, join communities, and participate in events
   - Staff users: Can moderate content and access additional features
   - Admin users: Full system access including approving communities and managing all content

2. **Role-Based Permissions**

   - Only community owners can manage community leaders and community settings
   - Community owners and leaders can create events for the community, and manage them
   - Community membership controls access to community-specific features
   - Event participation is controlled with capacity limits and join/leave permissions
   - Users can only delete their own posts or comments

3. **Safety Features**

   - Email verification for registration and address changes
   - User data protection with granular edit permissions
   - JWT authentication with secure token management
   - CSRF protection with trusted origins configuration
   - Secure password management requiring verification for changes
   - Comprehensive data cleanup when users delete their accounts

4. **Community Approval Process**
   - All new communities require admin approval before becoming active
   - Admins review community details via the admin panel at [http://localhost:8000/admin](http://localhost:8000/admin)
   - Communities remain in "inactive" state until explicitly approved

## Technical Implementation

### System Design

- **API Layer:** RESTful endpoints with comprehensive permission checks
- **Authentication:** Multi-stage JWT with token refresh and blacklisting
- **Data Management:** Transaction handling with proper error responses
- **Frontend-Backend Communication**: Secure API communication with CSRF protection
- **Notification System:** Event-driven alerts for social interactions, mentions, and content updates
- **Social Features:** Follow/unfollow system with automated notifications
- **Content Management:** Posts with mentions, hashtags, images, and comment threads
- **Container Deployment**: Docker-based environment for consistent development and deployment

### Tech Stack

- **Frontend**: SvelteKit, DaisyUI
- **Backend**: Django/Python
- **Database**: MySQL with normalised scheme
- **Containerization**: Docker

## External Services

Third-party email services are utilised in order to perform email verification for changing an email address and registering an account. To test this feature, please make a new user or change an existing user's email address to test this feature.

## Image Credits

All images used in this application are royalty-free stock photos sourced from [Unsplash](https://unsplash.com). These images are used for:

- User profile pictures
- Community header images
- Post attachments

## Maintainers

- Sude Fidan ([@sudefidan](https://github.com/sudefidan))
- James Lymbery ([@nerhZ](https://github.com/nerhZ))
- James Smith ([@jsmith3979](https://github.com/jsmith3979))
- John Higgins ([@depxas](https://github.com/depxas))
- Toby Meredith ([@Toby02](https://github.com/Toby02))

© 2025 UniHub
