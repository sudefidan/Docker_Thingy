# UniHub

UniHub is a university community platform designed to connect students, facilitate event organisation, and promote campus engagement.

## Getting Started

### GitHub Repo URL

[https://github.com/sudefidan/Docker_Thingy.git](https://github.com/sudefidan/Docker_Thingy.git)

### Access URLs

- **Frontend Application**: [http://localhost:5173/](http://localhost:5173/)
- **Admin Dashboard**: [http://localhost:8000/admin](http://localhost:8000/admin)

### User Accounts

The system comes pre-populated with 10 student accounts:

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

## Community Structure

The platform includes three pre-configured communities:

1. **Tech Innovators Hub** - For technology enthusiasts and developers
2. **Environmental Action Group** - Focused on sustainability and environmental initiatives
3. **Business Leaders Network** - For entrepreneurship and business networking

## External Services

Third-party email services are utilised in order to perform email verification for changing an email address and registering an account. To test this feature, please make a new user or change an existing user's email address to test this feature.

## Authorisation System

UniHub implements a robust authorisation system to ensure platform security and content moderation:

1. **Community Approval Process**
   - All new communities require admin approval before becoming active
   - Admins review community details via the admin panel at [http://localhost:8000/admin](http://localhost:8000/admin)
   - Communities remain in "inactive" state until explicitly approved

2. **User Access Levels**
   - Regular users: Can create content, join communities, and participate in events
   - Staff users: Can moderate content and access additional features
   - Admin users: Full system access including approving communities and managing all content

3. **Role-Based Permissions**
   - Only community owners can manage community leaders and community settings
   - Community owners and leaders can create events for the community, and manage them
   - Community membership controls access to community-specific features
   - Event participation is controlled with capacity limits and join/leave permissions
   - Users can only delete their own posts or comments

4. **Safety Features**
   - Email verification required for account registration and email changes
   - User profile data is protected with user-specific edit permissions
   - JWT authentication with secure token management
   - CSRF protection with trusted origins configuration
   - Secure password management requiring verification for changes
   - Comprehensive data cleanup when users delete their accounts

## Development Information

### Image Credits

All images used in this application are royalty-free stock photos sourced from [Unsplash](https://unsplash.com). These images are used for:

- User profile pictures
- Community header images
- Post attachments

### Tech Stack

- **Frontend**: SvelteKit, DaisyUI
- **Backend**: Django/Python
- **Database**: MySQL
- **Containerization**: Docker

## Maintainers

- Sude Fidan ([@sudefidan](https://github.com/sudefidan))
- James Lymbery ([@nerhZ](https://github.com/nerhZ))
- James Smith ([@jsmith3979](https://github.com/jsmith3979))
- John Higgins ([@depxas](https://github.com/depxas))
- Toby Meredith ([@Toby02](https://github.com/Toby02))

© 2025 UniHub
