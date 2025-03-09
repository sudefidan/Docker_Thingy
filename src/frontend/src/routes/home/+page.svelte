<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let access_token;

    onMount(() => {
        // Retrieve the access token from localStorage
        access_token = localStorage.getItem('access_token');

        if (access_token) {
            console.log("Access token found:", access_token);
            fetchProtectedData(access_token);
        } else {
			// Redirect to login if there's no access token
            console.log("No access token found. Redirecting to login...");
            goto('/login'); 
        }
    });

    // Function to fetch protected data using the access token
    const fetchProtectedData = async (token) => {
        const response = await fetch('http://127.0.0.1:8000/api/protected/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`  
            }
        });

        const data = await response.json();
        
        if (response.ok) {
            console.log('Data from protected endpoint:', data);
            // Handle the protected data (e.g., display user info)
        } else {
            console.error('Failed to access protected data:', data);
        }
    };
</script>

<main>
    <h1>Home uniHub</h1>
    <div id="responseMessage"></div>
    <div id="accessLevel"></div>
</main>
