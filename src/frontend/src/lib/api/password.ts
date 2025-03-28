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