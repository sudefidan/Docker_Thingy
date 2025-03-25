<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';

    let access_token;
    let users = [];
    let loggedInUserId;
    let postContent = "";
    let posts = [];
    let title = "";

    // on load of the page we ensure that these things are done, before the page is viewable
    // so for example we mostly do fetching and authorization checks to ensure the user is allowed to be
    // on this page, and we fetch akl the users and the posts.
	onMount(async () => {
		// Retrieve the access token from localStorage
		access_token = localStorage.getItem('access_token');

		if (!access_token) {
			// Redirect to login if no access token found
			goto('http://localhost:5173/');
		} else {
            loggedInUserId = getLoggedInUserIdFromToken(access_token);
			await fetchUsers();
            await fetchPosts();
		}
	});

    // Retrieve the logged-in user's ID from the access token
    function getLoggedInUserIdFromToken(token) {
        // Decode the token and extract the user ID (implementation depends on your token structure)
        // For example, if using JWT:
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.user_id;
    }
    // fetch the current users on the site
    const fetchUsers = async () => {
        const response = await fetch('http://127.0.0.1:8000/api/users/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${access_token}`
            }
        });

        const data = await response.json();
        if (response.ok) {
            console.log("all Users:", data);
        } else {
            console.error('Failed to fetch users:', data);
        }
    };

    // // Function to fetch protected data using the access token
    // const fetchProtectedData = async (token) => {
    //     const response = await fetch('http://127.0.0.1:8000/api/protected/', {
    //         method: 'GET',
    //         headers: {
    //             'Authorization': `Bearer ${token}`  
    //         }
    //     });

    //     const data = await response.json();
        
    //     if (response.ok) {
    //         console.log('Data from protected endpoint:', data);
    //         // Handle the protected data (e.g., display user info)
    //     } else {
    //         console.error('Failed to access protected data:', data);
    //     }
    // };



    // fetches current posts that users have made from the backend api
    const fetchPosts = async () => {
        const response = await fetch('http://127.0.0.1:8000/api/get_posts/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${access_token}`
            }
        });
        const data = await response.json();

        if (response.ok) {
            posts = data
            console.log('fetched posts:', posts);
            // Handle the protected data (e.g., display user info)
        } else {
            console.error('Failed to access posts:', data);
        }

    }
    // create post function to push the form data to the backend api
    const createPost = async() =>{
        if (!title.trim() || !postContent.trim()) return;

        const todayDate = new Date().toISOString().split('T')[0];


        const response = await fetch('http://127.0.0.1:8000/api/create_posts/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${access_token}`
				},
				body: JSON.stringify({
                    title: title,
                    content: postContent,
                    date: todayDate,
                    user_id: loggedInUserId
                })
			});
        if (response.ok) {
            const newPost = await response.json();
            posts.push(newPost);  
            title = '';  
            postContent = '';
            window.location.reload();
        } else {
            console.error('Failed to create post:', await response.json());
        }
    }
</script>

<main>
    <h1>Home uniHub</h1>

    <!-- Add input for the title here -->
    <form on:submit|preventDefault={createPost}>
        <input 
            type="text" 
            bind:value={title} 
            placeholder="Enter post title" 
            required 
        />
        <textarea 
            bind:value={postContent} 
            placeholder="Write your post..." 
            required 
        ></textarea>
        <button type="submit">Create Post</button>
    </form>
    <!-- display the title and content of the post -->
    <section>
        <h2>Posts</h2>
        {#each posts as p}
            <h3>{p.title}</h3>
            <p>{p.content}</p>
        {/each}
    </section>
</main>
