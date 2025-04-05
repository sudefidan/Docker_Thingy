// src/routes/(logged-in)/+layout.ts
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

export const load = async ({ fetch }) => {
	if (browser) {
		let accessToken = getAccessToken();
		const refreshToken = getRefreshToken();

        const refresh_request = fetch(`http://127.0.0.1:8000/api/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

		if (!accessToken) {
			// No access token, redirect to login
			console.error('No access token found.');
            const response = await refresh_request;
            if (response.ok) {
                const data = await response.json();
				const newAccessToken = data.access;
                accessToken = newAccessToken;

				setAccessToken(newAccessToken);
            } else {
			goto('/');
			return;
            }
		}

        console.log("OLD Refresh token: ", refreshToken)

		// Check if the token is about to expire
		const decodedToken = decodeJwt(accessToken);

        console.log("Access Token: ", decodedToken)
		if (!decodedToken) {
			console.error('Invalid access token.');
			goto('/');
			return;
		}

		if (!decodedToken.exp) {
			console.error('Access token is missing the "exp" claim.');
			goto('/');
			return;
		}

		const expirationTime = decodedToken.exp * 1000; // Convert to milliseconds
		const now = Date.now();
		const refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiration

		if (expirationTime - now < refreshThreshold) {
			// Token is about to expire, try to refresh
			try {
                const response = await refresh_request;
				if (response.ok) {
					const data = await response.json();
					const newAccessToken = data.access;

					setAccessToken(newAccessToken);
				} else {
					// Refresh failed, redirect to login
					console.error('Token refresh failed.');
					goto('/');
					return;
				}
			} catch (error) {
				console.error('Error refreshing token:', error);
				goto('/');
				return;
			}
		}
	}
	return {};
};

// Helper functions (you'll need to implement these)

function getAccessToken(): string | null {
	return localStorage.getItem('access_token');
}

function getRefreshToken(): string | null {
	return localStorage.getItem('refresh_token');
}

function setAccessToken(token: string): void {
	localStorage.setItem('access_token', token);
}

function setRefreshToken(token: string): void {
	localStorage.setItem('refresh_token', token);
}

function decodeJwt(token: string | null | undefined) {
    if (!token) {
        console.error('Error decoding JWT: Token is null or undefined');
        return null;
    }
    try {
        const parts = token.split('.');
        if (parts.length !== 3) {
            console.error('Error decoding JWT: Token is not a valid JWT');
            return null;
        }
        const base64Url = parts[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(atob(base64));
        return payload;
    } catch (error) {
        console.error('Error decoding JWT:', error);
        return null;
    }
}
