<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let access_token;
	let loggedInUserId;
	let postContent = '';
	let posts = [];
	let title = '';
	let filteredPosts = [];
	let searchTerm = ''; // Search term for filtering
	let subscribedCommunities = [];
	let selectedCommunityId = '';


	// Function to adjust the height of the textarea dynamically
	function adjustTextareaHeight(event) {
		const textarea = event.target;
		textarea.style.height = 'auto'; // Reset the height
		textarea.style.height = `${textarea.scrollHeight}px`; // Set the height to the scroll height
	}

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
			// await fetchCommunities();
			await fetchSubscribedCommunities();
		}
	});

	const fetchCommunities = async () => {
	try {
		const response = await fetch('http://127.0.0.1:8000/api/communities/');
		if (!response.ok) {
			throw new Error(`HTTP error! Status: ${response.status}`);
		}
		const data = await response.json();
		communities = data;
	} catch (error) {
		console.error('Failed to fetch communities:', error);
	}
};
const fetchSubscribedCommunities = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/subscribed_communities/', {
				method: 'GET',
				headers: { Authorization: `Bearer ${access_token}` }
			});

			if (response.ok) {
				const data = await response.json();
				subscribedCommunities = [...data.subscribed_communities];
				console.log('Fetched subscribed communities:', subscribedCommunities);
			} else {
				console.error('Failed to fetch subscribed communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};

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
				Authorization: `Bearer ${access_token}`
			}
		});

		const data = await response.json();
		if (response.ok) {
			console.log('all Users:', data);
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
			headers: { Authorization: `Bearer ${access_token}` }
		});
		const data = await response.json();
		if (response.ok) {
			posts = data;
		} else {
			console.error('Failed to fetch posts:', data);
		}
	};
	// create post function to push the form data to the backend api
	const createPost = async () => {
	if (!title.trim() || !postContent.trim()) return;

	const todayDate = new Date().toISOString().split('T')[0];

	const communityId = selectedCommunityId || null;

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
			user_id: loggedInUserId,
			community_id: selectedCommunityId
		})
	});
	if (response.ok) {
		const newPost = await response.json();
		posts.push(newPost);
		title = '';
		postContent = '';
		selectedCommunityId = '';
		window.location.reload();
	} else {
		console.error('Failed to create post:', await response.json());
	}
};
// filters posts from the search bar
$: filteredPosts = posts.filter(
	(p) =>
		p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
		p.content.toLowerCase().includes(searchTerm.toLowerCase())
	);

	function getCommunityName(communityId) {
    const community = subscribedCommunities.find(c => c.id === communityId);
    return community ? community.name : 'N/A'; 
  }

</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<!-- Top panel with search bar -->
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>
	<!-- Create Post -->
	<div class="card bg-base-100 w-full rounded-3xl mb-10">
		<div class="card-body bg-secondary rounded-3xl">
			<form id="post-form" class="space-y-4" on:submit|preventDefault={createPost}>
				<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="community" class="label">
							<span class="label-text">Select Community</span>
						</label>
						<div class="relative">
							<select
								id="community"
								bind:value={selectedCommunityId}
								class="select select-bordered custom-input"
							>
								<option value="" disabled selected>Select a community</option>
								{#each subscribedCommunities as community}
									<option value={community.id}>{community.name}</option>
								{/each}
							</select>
						</div>
						<label for="title" class="label">
							<span class="label-text">Title</span>
						</label>
						<div class="relative">
							<input
								type="text"
								id="title"
								bind:value={title}
								required
								class="input input-bordered custom-input"
								placeholder="What's the title of your post?"
							/>
						</div>
					</div>
				</div>
				<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="content" class="label">
							<span class="label-text">Content</span>
						</label>
						<div class="relative">
							<textarea
								id="content"
								bind:value={postContent}
								required
								class="input input-bordered text-area-input"
								placeholder="What's on your mind?"
								on:input={adjustTextareaHeight}
							></textarea>
						</div>
					</div>
				</div>
				<div class="form-control mb-2 flex justify-end">
					<button class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10" type="submit">
						Post
					</button>
				</div>
			</form>
		</div>
	</div>
	<!-- Posts Section -->
	<div class="grid grid-cols-1 w-full space-y-10">
		{#each filteredPosts as p}
			<div class="card bg-base-100 mb-10 shadow-4xl min-h-1/3 w-full rounded-3xl mb-4">
				<div class="card-body bg-secondary rounded-3xl">
					<h3 class="text-primary text-2xl font-bold">{p.title}</h3>
					<!-- display the community name if one has been given -->
					<p class="text-accent text-sm italic mb-2">
						Community posted in: {getCommunityName(p.community_id)}
					</p>
					<p
						class="text-base-100 pr-10 overflow-auto text-ellipsis"
						style="word-break: break-word;"
					>
						{p.content}
					</p>
				</div>
			</div>
		{/each}
	</div>
</main>
