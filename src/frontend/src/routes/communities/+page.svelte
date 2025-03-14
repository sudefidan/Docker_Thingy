<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let access_token;
    let name = '';
    let description = '';
    let category = '';

    onMount(() => {
        // Retrieve the access token from localStorage
        access_token = localStorage.getItem('access_token');

        if (!access_token) {
            // Redirect to login if no access token found
            goto('/login'); 
        }
    });

    const submitForm = async (event) => {
        event.preventDefault(); 
  
        if (!name || !description || !category) {
            console.log("All fields are required!");
            return; 
        }

        // Prepare the form data
        const data = {
            name: name,
            description: description,
            category: category
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/api/create_community/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${access_token}`  
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                // Redirect to the created community page
                window.location.reload()
            } else {
                console.error('Error creating community:', result.error || 'Something went wrong');
            }
        } catch (error) {
            console.error('Network Error:', error.message);
        }
    };

    // Optionally fetch protected data (not necessary for form submission)
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
        } else {
            console.error('Failed to access protected data:', data);
        }
    };
</script>

<main>
    <h1>Communities uniHub</h1>

    <h2>Create a Community</h2>
    
    <form id="community-form" on:submit={submitForm}>
        <label for="name">Community Name:</label>
        <input type="text" id="name" bind:value={name} required><br><br>
        
        <label for="description">Description:</label>
        <textarea id="description" bind:value={description} required></textarea><br><br>
        
        <label for="category">Category:</label>
        <input type="text" id="category" bind:value={category} required><br><br>
        
        <button type="submit">Create Community</button>
    </form>

    <div id="message"></div>
</main>
