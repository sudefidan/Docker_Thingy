import { goto } from '$app/navigation';

// helper function to get the access token
function getToken(): string {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }
    return token;
}

export interface UserProfile {
    profile_picture: string;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
    social_type: string[];
    social_username: string[];
    about: string;
    interests: string[];
}

export async function fetchUserProfile(): Promise<UserProfile> {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }

    const response = await fetch('http://localhost:8000/api/user-profile/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    if (!response.ok) {
        throw new Error('Failed to fetch profile');
    }

    const data = await response.json();
    return {
        ...data,
        social_type: data.social_type || [],
        social_username: data.social_username || []
    };
}

export async function updateProfile(profile: {
    username: string;
    first_name: string;
    last_name: string;
    email: string;
}): Promise<void> {
    try {
        const response = await fetch('http://localhost:8000/api/update-profile/', {
        method: 'PUT',
        headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(profile)
    });

    if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update profile');
        }

        // profile updated successfully
        return;
    } catch (error) {
        console.error('Error updating profile:', error);
        throw error;
    }
}

export async function updateProfilePicture(base64Image: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (!token) {
        goto('/login');
        throw new Error('Not authenticated');
    }

    const response = await fetch('http://localhost:8000/api/upload-profile-picture/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            profile_picture: base64Image
        })
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to update profile picture');
    }

    const data = await response.json();
    return data;
}

// handles password change requests
export async function changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
    const response = await fetch('http://localhost:8000/api/change-password/', {
        method: 'POST',
        headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword
        })
    });

    if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to change password');
        }

        // password changed successfully
        return;
    } catch (error) {
        console.error('Error changing password:', error);
        throw error;
    }
}

// Social media icons
export const socialMediaIcons = {
    instagram: `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="size-6"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.012-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`,
    linkedin: `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="size-6"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>`,
    twitter: `<svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24" class="size-6"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>`
};

export interface SocialMedia {
    name: string;
    svg: string;
}

export const socialMedias: SocialMedia[] = [
    { name: 'instagram', svg: socialMediaIcons.instagram },
    { name: 'linkedin', svg: socialMediaIcons.linkedin },
    { name: 'twitter', svg: socialMediaIcons.twitter }
];

export async function updateSocialMedia(socialType: string, socialUsername: string) {
    try {
        const token = getToken();
        const response = await fetch('http://localhost:8000/api/update-social-media/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                social_type: socialType,
                social_username: socialUsername
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update social media');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating social media:', error);
        throw error;
    }
}

export async function removeSocialMedia(socialType: string): Promise<void> {
    try {
        const response = await fetch('http://localhost:8000/api/update-social-media/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({
                social_type: socialType
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to remove social media');
        }
    } catch (error) {
        console.error('Error removing social media:', error);
        throw error;
    }
}

// handles about section updates
// sends the new about text to the backend
// returns the updated about section data
export async function updateAbout(about: string): Promise<{ message: string; about: string }> {
    try {
        const response = await fetch('http://localhost:8000/api/update-about/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ about })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update about section');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating about section:', error);
        throw error;
    }
}

// handles interests updates
// sends the new interests array to the backend
// returns the updated interests data
export async function updateInterests(interests: string[]): Promise<{ message: string; interests: string[] }> {
    try {
        const response = await fetch('http://localhost:8000/api/update-interests/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify({ interests })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update interests');
        }

        return await response.json();
    } catch (error) {
        console.error('Error updating interests:', error);
        throw error;
    }
} 