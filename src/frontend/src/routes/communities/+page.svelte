<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let access_token;
    let name = '';
    let description = '';
    let category = '';
    let users = []; 
    let selectedUsers = []; 

    onMount(async () => {
        // Retrieve the access token from localStorage
        access_token = localStorage.getItem('access_token');

        if (!access_token) {
            // Redirect to login if no access token found
            goto('/login'); 
        } else {
            await fetchUsers(); 
        }
    });

    // Fetch users from the API
    const fetchUsers = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/users/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${access_token}`
                }
            });

            if (response.ok) {
                users = await response.json();
            } else {
                console.error('Failed to fetch users');
            }
        } catch (error) {
            console.error('Network error:', error.message);
        }
    };

    const submitForm = async (event) => {
        event.preventDefault(); 

        if (!name || !description || !category) {
            console.log("All fields are required!");
            return; 
        }

        const data = {
            name,
            description,
            category,
            leader_ids: selectedUsers 
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
                window.location.reload();  
            } else {
                console.error('Error creating community:', result.error || 'Something went wrong');
            }
        } catch (error) {
            console.error('Network Error:', error.message);
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

        <fieldset>
            <legend>Select Community Leaders (optional):</legend>
            {#each users as user}
                <div>
                    <input type="checkbox" id="user-{user.id}" bind:group={selectedUsers} value={user.id}>
                    <label for="user-{user.id}">{user.username}</label>
                </div>
            {/each}
        </fieldset><br><br>

        <button type="submit">Create Community</button>
    </form>
</main>

