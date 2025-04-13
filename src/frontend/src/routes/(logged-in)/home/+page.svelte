<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
  
	let access_token;
	let loggedInUserId;
	let postContent = '';
	let title = '';
	let posts = [];
	let filteredPosts = [];
	let searchTerm = ''; 
	let subscribedCommunities = [];
	let selectedCommunityId = '';
	let postCreationError = null;
	let postCreationSuccess = false;
	// let allCommunities = [];

	let userProfile = {
	  profile_picture: '',
	  username: '',
	  first_name: '',
	  last_name: '',
	  email: '',
	  social_type: [],
	  social_username: [],
	  about: '',
	  interests: []
	};
  
	// Function to adjust the height of the textarea dynamically
	function adjustTextareaHeight(event) {
	  const textarea = event.target;
	  textarea.style.height = 'auto'; // Reset the height
	  textarea.style.height = `${textarea.scrollHeight}px`; // Set the height to the scroll height
	}
  
	// on load of the page we ensure that these things are done, before the page is viewable
	onMount(async () => {
	  access_token = localStorage.getItem('access_token');
	  if (!access_token) {
		goto('http://localhost:5173/');
	  } else {
		loggedInUserId = getLoggedInUserIdFromToken(access_token);
		await fetchPosts();
		await fetchSubscribedCommunities();
		// await fetchAllCommunities();
	  }
	});
  
	// Fetch the subscribed communities of the current logged-in user
	const fetchSubscribedCommunities = async () => {
	  try {
		const response = await fetch('http://127.0.0.1:8000/api/subscribed_communities/', {
		  method: 'GET',
		  headers: { Authorization: `Bearer ${access_token}` }
		});
  
		if (response.ok) {
		  const data = await response.json();
		  subscribedCommunities = [...data.subscribed_communities];
		} else {
		  console.error('Failed to fetch subscribed communities');
		}
	  } catch (error) {
		console.error('Network error:', error.message);
	  }
	};

// 	const fetchAllCommunities = async () => {
//   try {
//     const response = await fetch('http://127.0.0.1:8000/api/communities/', {
//       method: 'GET',
//       headers: { Authorization: `Bearer ${access_token}` }
//     });

//     if (response.ok) {
//       const data = await response.json();
//       allCommunities = data; // Store communities in the allCommunities array
//       console.log("All communities:", allCommunities);
//     } else {
//       console.error('Failed to fetch all communities');
//     }
//   } catch (error) {
//     console.error('Error fetching all communities:', error);
//   }
// };


  
	// Fetch all posts made

	const fetchPosts = async () => {
  		const response = await fetch('http://127.0.0.1:8000/api/get_posts/', {
    		method: 'GET',
   			headers: { Authorization: `Bearer ${access_token}` }
  		});

  		const data = await response.json();
  		if (response.ok) {
    		posts = await Promise.all(data.map(async (post) => {
      		const userProfile = await fetchUserProfileForPost(post.user_id);
      		return { ...post, userProfile };
    	}));
  		} else {
    		console.error('Failed to fetch posts:', data);
  		}
	};

  
	// Fetch the user's profile for a given post
	const fetchUserProfileForPost = async (userId) => {
	  try {
		const response = await fetch(`http://127.0.0.1:8000/api/user-profile/${userId}/`, {
		  method: 'GET',
		  headers: { Authorization: `Bearer ${access_token}` }
		});
  
		if (response.ok) {
		  const profileData = await response.json();
		  return {
			username: profileData.username,
			profile_picture: profileData.profile_picture || '', // Ensure the Base64 profile picture is set
			first_name: profileData.first_name,
			last_name: profileData.last_name,
			email: profileData.email
		  };
		}
	  } catch (error) {
		console.error('Error fetching user profile for post:', error);
	  }
	  return {};
	};
  
	// Function to create a new post
	const createPost = async () => {
	  if (!title.trim() || !postContent.trim()) return;
  
	  const todayDate = new Date().toISOString().split('T')[0];
  
	  try {
		const response = await fetch('http://127.0.0.1:8000/api/create_posts/', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${access_token}`,
		  },
		  body: JSON.stringify({
			title: title,
			content: postContent,
			date: todayDate,
			user_id: loggedInUserId,
			community_id: selectedCommunityId || null,
		  }),
		});
  
		if (response.ok) {
		  const newPost = await response.json();
		  posts.push(newPost); 
		  title = ''; 
		  postContent = '';
		  selectedCommunityId = '';
		  postCreationSuccess = true;
		  postCreationError = null; 
		  window.location.reload();
		} else {
		  const error = await response.json();
		  postCreationError = error.message || 'Failed to create post.';
		  postCreationSuccess = false;
		}
	  } catch (error) {
		postCreationError = 'Error creating post. Please try again.';
		postCreationSuccess = false;
	  }
	};
  
	// Filters posts based on the search term
	$: filteredPosts = posts.filter(
	  (p) =>
		p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
		p.content.toLowerCase().includes(searchTerm.toLowerCase())
	);
  
	// Retrieve the logged-in user's ID from the access token
	function getLoggedInUserIdFromToken(token) {
	  const payload = JSON.parse(atob(token.split('.')[1]));
	  return payload.user_id;
	}
	// allows users to delete the posts
	const deletePost = async (postId) => {
  	const confirmDelete = confirm('Are you sure you want to delete this post?');
  	if (!confirmDelete) return;

  		try {
		const response = await fetch(`http://127.0.0.1:8000/api/delete_post/${postId}/`, {
	  	method: 'DELETE',
	  	headers: {
		Authorization: `Bearer ${access_token}`,
	  },
	});

	if (response.ok) {
	  posts = posts.filter(post => post.id !== postId); 
	} else {
	  console.error('Failed to delete post');
	  alert('Failed to delete post');
	}
  	} catch (error) {
	console.error('Error deleting post:', error);
	alert('An error occurred while deleting the post');
  	}
	};






  </script>
  
  <main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<!-- Top panel with search bar -->
	<div class="top-panel">
	  <input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>
  
	<!-- Create Post Form -->
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
  
	<!-- Success/Error Message -->
	{#if postCreationError}
	  <div class="alert alert-error">{postCreationError}</div>
	{/if}
  
	{#if postCreationSuccess}
	  <div class="alert alert-success">Your post has been created successfully!</div>
	{/if}
  
	<!-- Posts Section -->
	<div class="grid grid-cols-1 w-full space-y-10">
	  {#each filteredPosts as p}
		<div class="card bg-base-100 mb-10 shadow-4xl min-h-1/3 w-full rounded-3xl mb-4">
		  <div class="card-body bg-secondary rounded-3xl">
			<h3 class="text-primary text-2xl font-bold">{p.title}</h3>
			<p class="text-accent text-sm italic mb-2">Community posted in: {p.community_name}</p>
			<div class="profile">
			  {#if p.userProfile.profile_picture}
				<img src={`data:image/jpeg;base64,${p.userProfile.profile_picture}`} alt="Profile Picture" class="profile-picture" />
			  {:else}
				<!-- show the default picture -->
			  {/if}
			</div>
			<p class="text-accent text-sm mb-2">Posted by: {p.userProfile.username}</p>
			<p class="text-base-100 pr-10 overflow-auto text-ellipsis" style="word-break: break-word;">
			  {p.content}
			</p>

			{#if p.user_id === loggedInUserId}
			<button
			  on:click={() => deletePost(p.id)}
			  class="btn btn-error text-white mt-3">
			  Delete Post
			</button>
		  {/if}
		  </div>
		</div>
	  {/each}
	</div>
  </main>
  