<script>
	import { onMount, onDestroy } from 'svelte';
	import { goto } from '$app/navigation';
	import BinIcon from '../../../assets/BinIcon.svelte';
	import MediaIcon from '../../../assets/MediaIcon.svelte';
	import ProfilePictureIcon from '../../../assets/ProfilePictureIcon.svelte';
	import AddIconNoCircle from '../../../assets/AddIconNoCircle.svelte';
	import LikeIcon from '../../../assets/LikeIcon.svelte';
	import LikedIcon from '../../../assets/LikedIcon.svelte';
	import CommentIcon from '../../../assets/CommentIcon.svelte';

	let access_token;
	let loggedInUserId;
	let postContent = '';
	let title = '';
	let posts = [];
	let filteredPosts = [];
	let searchTerm = '';
	let subscribedCommunities = [];
	let selectedCommunityId = '';
	let postImage = null; 
	let selectedImage = null; 
	let showPostModal = false; 
	let currentTime = new Date();
	let postComments = {};
	let activeCommentPostId = null;
	let loadingComments = false;
	let newComment = {};
	let tempComment = '';

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

	// Function to format the date
	function formatDate(dateString) {
		const date = new Date(dateString);
		const diffInMs = currentTime - date; // Difference in milliseconds
		const diffInSeconds = Math.floor(diffInMs / 1000); // Difference in seconds
		const diffInMinutes = Math.floor(diffInSeconds / 60); // Difference in minutes
		const diffInHours = Math.floor(diffInMinutes / 60); // Difference in hours
		const diffInDays = Math.floor(diffInHours / 24); // Difference in days

		if (diffInSeconds < 60) {
			// If less than a minute, show seconds as "sec"
			return 'Just now';
		} else if (diffInMinutes < 60) {
			// If less than an hour, show minutes as "m"
			return `${diffInMinutes}m`;
		} else if (diffInHours < 24) {
			// If less than 24 hours, show hours as "h"
			return `${diffInHours}h`;
		} else if (diffInDays < 7) {
			// If within the last week, show days as "d"
			return `${diffInDays}d`;
		} else {
			// Otherwise, format as "MMM dd" or "MMM dd, yyyy" if not the current year
			const currentYear = new Date().getFullYear();
			const options = {
				month: 'short',
				day: 'numeric'
			};

			if (date.getFullYear() !== currentYear) {
				options.year = 'numeric';
			}

			return new Intl.DateTimeFormat('en-US', options).format(date);
		}
	}

	// Update the current time every second
	let interval;
	onMount(() => {
		interval = setInterval(() => {
			currentTime = new Date(); // Update the current time
		}, 1000); // Update every second
	});

	onDestroy(() => {
		clearInterval(interval); // Clear the interval when the component is destroyed
	});

	// Function to toggle the post creation modal
	const togglePostModal = () => {
		if (showPostModal) {
			// Reset the image preview when closing the modal
			postImage = null;
		}
		showPostModal = !showPostModal;
	};

	// Function to open the image modal
	// This function is called when an image is clicked
	const openImageModal = (imageUrl) => {
		selectedImage = imageUrl;
	};

	// Function to close the image modal
	// This function is called when the modal background is clicked
	const closeImageModal = () => {
		selectedImage = null;
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
			await fetchUserProfile();
			await fetchPosts();
			await fetchSubscribedCommunities();
			await fetchPosts();
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

	// Fetch all posts made
	// only include posts from subscribed communities
	const fetchPosts = async () => {
		const response = await fetch('http://127.0.0.1:8000/api/get_posts/', {
			method: 'GET',
			headers: { Authorization: `Bearer ${access_token}` }
		});

		const data = await response.json();
		if (response.ok) {
			posts = await Promise.all(
				data
					.filter((post) => !post.community_id || isUserSubscribedToCommunity(post.community_id)) // Only include posts from subscribed communities
					.map(async (post) => {
						const userProfile = await fetchUserProfileForPost(post.user_id);
						return { ...post, userProfile };
					})
			);
			console.log('Posts:', posts);
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
					profile_picture: profileData.profile_picture || '',
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

	// Function to handle image selection
	const handleImageChange = (event) => {
		postImage = event.target.files[0];
	};

	// Function to create a new post
	const createPost = async () => {
		if (!title.trim() || !postContent.trim()) return;

		const todayDate = new Date().toISOString().split('T')[0];

		try {
			const formData = new FormData();
			formData.append('title', title);
			formData.append('content', postContent);
			formData.append('date', todayDate);
			formData.append('user_id', loggedInUserId);
			formData.append('community_id', selectedCommunityId || null);
			if (postImage) {
				formData.append('image', postImage); // Append the image file
			}

			const response = await fetch('http://127.0.0.1:8000/api/create_posts/', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`
				},
				body: formData // Use FormData for file uploads
			});

			if (response.ok) {
				const newPost = await response.json();
				posts.push(newPost);
				title = '';
				postContent = '';
				selectedCommunityId = '';
				postImage = null; // Reset the image input
				window.location.reload();
			} else {
				const error = await response.json();
				alert('Failed to create post:', error);
			}
		} catch (error) {
			alert('Error creating post:', error);
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
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok) {
				posts = posts.filter((post) => post.id !== postId);
			} else {
				console.error('Failed to delete post');
				alert('Failed to delete post');
			}
		} catch (error) {
			console.error('Error deleting post:', error);
			alert('An error occurred while deleting the post');
		}
	};
	// checks if user is subscribed to that community
	function isUserSubscribedToCommunity(communityId) {
		return subscribedCommunities.some((community) => community.id === communityId);
	}
	// retrieves the users details, but more importantly their profile picture for the creation of a post
	const fetchUserProfile = async () => {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/user-profile/${loggedInUserId}/`, {
				method: 'GET',
				headers: { Authorization: `Bearer ${access_token}` }
			});

			if (response.ok) {
				const profileData = await response.json();
				userProfile = {
					username: profileData.username,
					profile_picture: profileData.profile_picture || '',
					first_name: profileData.first_name,
					last_name: profileData.last_name,
					email: profileData.email,
					social_type: profileData.social_type,
					social_username: profileData.social_username,
					about: profileData.about,
					interests: profileData.interests
				};
			}
		} catch (error) {
			console.error('Error fetching user profile:', error);
		}
	};

	async function toggleComments(postId) {
    if (activeCommentPostId === postId) {
        activeCommentPostId = null;
    } else {
        activeCommentPostId = postId;

        if (!postComments[postId]) {
            loadingComments = true;
            try {
                let token = localStorage.getItem("access_token");
                let refreshToken = localStorage.getItem("refresh_token");

                if (!token) {
                    console.error("No access token found");
                    postComments[postId] = [];
                    // Initialize newComment for this postId
                    if (!newComment[postId]) {
                        newComment[postId] = '';
                    }
                    return;
                }

                // Try to fetch comments with the current access token
                let res = await fetch(`http://127.0.0.1:8000/comments/${postId}/`, {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                });

                // If access token is expired (401), try refreshing the token
                if (res.status === 401 && refreshToken) {
                    // Refresh the token
                    const refreshRes = await fetch("http://127.0.0.1:8000/api/token/refresh/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            refresh: refreshToken
                        })
                    });

                    if (refreshRes.ok) {
                        const data = await refreshRes.json();
                        token = data.access;  // Get the new access token
                        // Save the new token
                        localStorage.setItem("accessToken", token);

                        // Retry fetching comments with the new token
                        res = await fetch(`http://127.0.0.1:8000/comments/${postId}/`, {
                            method: "GET",
                            headers: {
                                "Authorization": `Bearer ${token}`,
                                "Content-Type": "application/json"
                            }
                        });
                    } else {
                        console.error("Failed to refresh the token");
                        postComments[postId] = [];
                        // Initialize newComment for this postId
                        if (!newComment[postId]) {
                            newComment[postId] = '';
                        }
                        return;
                    }
                }

                // Check if request was successful and initialize newComment
                if (res.ok) {
                    const data = await res.json();
                    postComments[postId] = data;
                    // Initialize newComment for this postId
                    if (!newComment[postId]) {
                        newComment[postId] = '';
                    }
                } else {
                    console.error("Failed to fetch comments:", await res.text());
                    postComments[postId] = [];
                    // Initialize newComment for this postId
                    if (!newComment[postId]) {
                        newComment[postId] = '';
                    }
                }
            } catch (err) {
                console.error("Error loading comments:", err);
                postComments[postId] = [];
                // Initialize newComment for this postId
                if (!newComment[postId]) {
                    newComment[postId] = '';
                }
            } finally {
                loadingComments = false;
            }
        } else {
            // Initialize newComment for this postId if it doesn't exist
            if (!newComment[postId]) {
                newComment[postId] = '';
            }
        }
    }
}
const postComment = async (postId) => {
        const commentText = newComment[postId]?.trim();
        if (!commentText) {
            alert('Please enter a comment.');
            return;
        }

        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('No access token found.');
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/comments/${postId}/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ comment: commentText }),
            });

            if (response.ok) {
                const newCommentData = await response.json();
                // Optimistically update the UI by adding the new comment to the postComments array
                postComments[postId] = [...(postComments[postId] || []), newCommentData];
                // Clear the comment input field
                newComment[postId] = '';
            } else {
                const errorData = await response.json();
                console.error('Failed to post comment:', errorData);
                alert('Failed to post comment.');
                // Optionally, you could retry the comment submission or handle the error differently
            }
        } catch (error) {
            console.error('Error posting comment:', error);
            alert('An error occurred while posting the comment.');
        }
    };

    const likeUnlikePost = async (postId) => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            goto('http://localhost:5173/'); // Or handle unauthenticated state
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/posts/${postId}/like/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                // Update the local posts array
                posts = posts.map((post) => {
                    if (post.id === postId) {
                        const newUserLiked = !post.user_liked;
                        const newLikeCount = newUserLiked ? post.like_count + 1 : post.like_count - 1;
                        return { ...post, user_liked: newUserLiked, like_count: newLikeCount };
                    }
                    return post;
                });
                filteredPosts = filteredPosts.map((post) => {
                    if (post.id === postId) {
                        const newUserLiked = !post.user_liked;
                        const newLikeCount = newUserLiked ? post.like_count + 1 : post.like_count - 1;
                        return { ...post, user_liked: newUserLiked, like_count: newLikeCount };
                    }
                    return post;
                });
            } else {
                console.error('Failed to like/unlike post:', await response.text());
                alert('Failed to like/unlike post.');
            }
        } catch (error) {
            console.error('Error liking/unliking post:', error);
            alert('An error occurred while liking/unliking the post.');
        }
    };
</script>

<main class="px-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>

	<!-- Post Creation Modal -->
	{#if showPostModal}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
			on:click={togglePostModal}
		>
			<div
				class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-5xl"
				on:click|stopPropagation
			>
				<form id="post-form" class="space-y-4" on:submit|preventDefault={createPost}>
					<div class="flex items-start">
						<!-- TODO: Show User's Profile Picture -->
						{#if userProfile.profile_picture}
							<img
								src={`data:image/jpeg;base64,${userProfile.profile_picture}`}
								alt="Profile Picture"
								class="profile-picture"
							/>
						{:else}
							<ProfilePictureIcon size={50} class="profile-picture" />
						{/if}

						<!-- Post Input Fields -->
						<div class="ml-5 mt-0 flex flex-col w-full">
							<!-- Community selection dropdown -->
							<select
								id="community"
								bind:value={selectedCommunityId}
								class="select select-bordered custom-input mb-3 placeholder-selected"
							>
								<option value="" disabled selected>Everyone</option>
								{#each subscribedCommunities as community}
									<option value={community.id}>{community.name}</option>
								{/each}
							</select>
							<!-- Title Field -->
							<input
								type="text"
								id="title"
								bind:value={title}
								required
								class="input input-bordered custom-input w-full mb-3"
								placeholder="What's the title of your post?"
							/>
							<!-- Content Field -->
							<textarea
								id="content"
								bind:value={postContent}
								required
								class="input input-bordered text-area-input w-full min-h-[150px] mb-3"
								placeholder="What's on your mind?"
								on:input={adjustTextareaHeight}
							></textarea>
							<!-- Image Preview -->
							{#if postImage}
								<div class="mb-3 flex justify-center">
									<img
										src={URL.createObjectURL(postImage)}
										alt="Selected Image"
										class="rounded-md min-w-[20%] max-w-[25%] h-auto"
									/>
								</div>
							{/if}
							<!-- Add Icons-->
							<div class="form-control flex flex-col gap-5 sm:flex-row">
								<!-- Add Image -->
								<div class="relative tooltip-container">
									<label
										for="file-upload"
										class="cursor-pointer flex items-center justify-center text-base-100 hover:text-primary"
									>
										<MediaIcon size={28} />
									</label>
									<!-- Hidden File Input -->
									<input
										id="file-upload"
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleImageChange}
									/>
									<span class="tooltip">Add Media</span>
								</div>
							</div>
							<!-- Add Post Button -->
							<div class="flex justify-end w-full">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									type="submit"
								>
									Post
								</button>
							</div>
						</div>
					</div>
				</form>
			</div>
		</div>
	{/if}
	<!-- Posts Section -->
	{#each filteredPosts as p}
		<div class="card bg-base-100 shadow-4xl w-full rounded-3xl mb-5">
			<div class="card-body bg-secondary rounded-3xl">
				<!-- Community name next to the icon -->
				<div class="flex items-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						fill="var(--color-base-content)"
						viewBox="0 0 24 24"
						class="w-6 h-6 mr-2 ml-8 mb-0 mt-0"
					>
						<path
							d="M8.25 6.75a3.75 3.75 0 1 1 7.5 0 3.75 3.75 0 0 1-7.5 0ZM15.75 9.75a3 3 0 1 1 6 0 3 3 0 0 1-6 0ZM2.25 9.75a3 3 0 1 1 6 0 3 3 0 0 1-6 0ZM6.31 15.117A6.745 6.745 0 0 1 12 12a6.745 6.745 0 0 1 6.709 7.498.75.75 0 0 1-.372.568A12.696 12.696 0 0 1 12 21.75c-2.305 0-4.47-.612-6.337-1.684a.75.75 0 0 1-.372-.568 6.787 6.787 0 0 1 1.019-4.38Z"
						/>
						<path
							d="M5.082 14.254a8.287 8.287 0 0 0-1.308 5.135 9.687 9.687 0 0 1-1.764-.44l-.115-.04a.563.563 0 0 1-.373-.487l-.01-.121a3.75 3.75 0 0 1 3.57-4.047ZM20.226 19.389a8.287 8.287 0 0 0-1.308-5.135 3.75 3.75 0 0 1 3.57 4.047l-.01.121a.563.563 0 0 1-.373.486l-.115.04c-.567.2-1.156.349-1.764.441Z"
						/>
					</svg>
					<p class="text-accent text-sm">{p.community_name}</p>

					<!-- Remove button for the post -->
					{#if p.user_id === loggedInUserId}
						<div class="flex flex-end justify-end">
							<div class="tooltip-container">
								<button
									type="submit"
									class="hover:text-primary flex items-center"
									on:click={() => deletePost(p.id)}
								>
									<BinIcon size={20} />

									<span class="tooltip">Delete Post</span>
								</button>
							</div>
						</div>
					{/if}
				</div>
				<!-- Post content -->
				<div class="flex items-start">
					{#if p.userProfile.profile_picture}
						<img
							src={`data:image/jpeg;base64,${p.userProfile.profile_picture}`}
							alt="Profile Picture"
							class="profile-picture"
						/>
					{:else}
						<ProfilePictureIcon size={50} class="profile-picture" />
					{/if}
					<div class="ml-2 mt-0 flex flex-col">
						<p class="text-base-100 text-lg font-bold">
							{p.userProfile.first_name}
							{p.userProfile.last_name}
							<span class="font-normal">@{p.userProfile.username}</span>
							<span class="font-normal">· {formatDate(p.date)}</span>
						</p>
						<h3 class="text-primary text-lg font-bold">{p.title}</h3>
						<p class="text-base-100 overflow-auto text-ellipsis" style="word-break: break-word;">
							{p.content}
						</p>
						{#if p.id}
							<img
								src={`http://127.0.0.1:8000/post_image/${p.id}/`}
								alt="Post Image"
								class="mt-4 rounded-md"
								style="max-width: 30%; height: auto;"
								on:error={(event) => (event.target.style.display = 'none')}
								on:click={() => openImageModal(`http://127.0.0.1:8000/post_image/${p.id}/`)}
							/>
						{/if}
					</div>
				</div>
				<div class="flex items-center gap-x-4">
                    <button class="flex items-center gap-x-1" on:click={() => likeUnlikePost(p.id)}>
                        {#if p.user_liked}
                            <LikedIcon />
                        {:else}
                            <LikeIcon />
                        {/if}
                        <p>{p.like_count !== undefined ? p.like_count : 0} Likes</p>
                    </button>
					<div class="flex items-center gap-x-1 cursor-pointer" on:click={() => toggleComments(p.id)}>
						<CommentIcon />
						<p>{p.comment_count !== undefined ? p.comment_count : 'View'} Comments</p>
					</div>
				</div>
				{#if activeCommentPostId === p.id}
				    <div class="mt-4 bg-base-200 p-4 rounded-xl">
				        {#if loadingComments}
				            <p class="italic">Loading comments...</p>
				        {:else if postComments[p.id]?.length}
				            <h4 class="text-base-content font-semibold mb-2">Comments:</h4>
				            {#each postComments[p.id] as c}
				                <p class="text-base-content mb-1">
				                    <strong>@{c.user.username}</strong>: {c.comment}
				                    <span class="text-sm text-gray-500 ml-2">{new Date(c.timestamp).toLocaleString()}</span>
				                </p>
				            {/each}
				        {:else}
				            <p class="text-base-content italic">No comments yet.</p>
				        {/if}
				
				        <div class="mt-4">
					<input
					type="text"
					placeholder="Write a comment..."
					class="input input-bordered w-full mb-2"
					bind:value={newComment[p.id]}
				/>
				            <button class="btn btn-primary btn-sm" on:click={() => postComment(p.id)}>Post Comment</button>
				        </div>
				    </div>
				{/if}
        </div>
    </div>
{/each}

	<!-- Modal for enlarged image -->
	{#if selectedImage}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 flex items-center justify-center z-40 p-10"
			on:click={closeImageModal}
		>
			<img src={selectedImage} alt="Enlarged Image" class="max-w-full max-h-full rounded-md" />
		</div>
	{/if}

	<!-- Floating Add Button -->
	<button
		class="fixed bottom-5 right-5 bg-primary text-secondary p-4 rounded-full shadow-lg hover:bg-primary-focus z-50"
		on:click={togglePostModal}
	>
		<AddIconNoCircle size={28} />
	</button>



</main>
