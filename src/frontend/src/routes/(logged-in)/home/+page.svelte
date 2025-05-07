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
	import UniCapIcon from '../../../assets/UniCapIcon.svelte';
	import { socialMedias } from '$lib/api/profile';

	let access_token; // Access token for authentication
	let loggedInUserId; // ID of the logged-in user
	let postContent = ''; // Content of the post
	let title = ''; // Title of the post
	let posts = []; // Array to hold posts
	let filteredPosts = []; // Filtered posts based on search term
	let searchTerm = ''; // Search term for filtering posts
	let subscribedCommunities = []; // Array to hold subscribed communities
	let selectedCommunityId = ''; // ID of the selected community for the post
	let postImage = null; // Image for the post
	let selectedImage = null; // Image selected for preview
	let showPostModal = false; // Flag to show/hide the post creation modal
	let currentTime = new Date(); // Current time for date formatting
	let postComments = {}; // Object to hold comments for each post
	let activeCommentPostId = null; // ID of the post for which comments are being loaded
	let loadingComments = false; // Flag to indicate if comments are being loaded
	let newComment = {}; // Object to hold new comment text for each post
	let activeHashtag = null; // Active hashtag for filtering posts
	let allPosts = []; // Full list of posts
	let users = []; // Array to hold all users
	let usersList = []; // List of users for the dropdown
	let showUserProfileModal = false; // Flag to show/hide the user profile modal
	let selectedUserId = null; // ID of the selected user for profile viewing
	let modalLoading = false; // Flag to indicate if the user profile modal is loading
	let modalError = false; // Flag to indicate if there was an error loading the user profile
	let modalUserProfile = null; // Hold user profile data for the modal

	// User profile object to hold user details
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

	// Dropdown object to manage the mention dropdown
	let mentionDropdown = {
		show: false,
		position: { top: 0, left: 0 },
		filteredUsers: [],
		query: '',
		selectedIndex: 0
	};
	let textareaElement; // Reference to the textarea element for mention handling
	let commentMentionDropdown = {}; // Object to hold mention dropdown state for each post's comment
	let commentTextareaElements = {}; // Object to hold textarea elements for each post's comment

	// Function to handle mention in comments
	function handleCommentMention(event, postId) {
		const text = event.target.value;
		const cursorPosition = event.target.selectionStart;

		// Store textarea element reference
		if (!commentTextareaElements[postId]) {
			commentTextareaElements[postId] = event.target;
		}

		// Initialize dropdown for this post if it doesn't exist
		if (!commentMentionDropdown[postId]) {
			commentMentionDropdown[postId] = {
				show: false,
				position: { top: 0, left: 0 },
				filteredUsers: [],
				query: '',
				selectedIndex: 0
			};
		}

		// Check if we're in a potential mention context
		const textBeforeCursor = text.substring(0, cursorPosition);
		const mentionMatch = textBeforeCursor.match(/@(\w*)$/);

		if (mentionMatch && commentTextareaElements[postId]) {
			const query = mentionMatch[1].toLowerCase();
			commentMentionDropdown[postId].query = query;

			// Filter users based on query
			commentMentionDropdown[postId].filteredUsers = usersList.filter((user) =>
				user.name.toLowerCase().includes(query)
			);

			try {
				// Calculate position for dropdown
				const textareaRect = commentTextareaElements[postId].getBoundingClientRect();
				const lineHeight =
					parseInt(getComputedStyle(commentTextareaElements[postId]).lineHeight) || 20;

				// Position dropdown below the current line
				commentMentionDropdown[postId].position = {
					left: textareaRect.left,
					top: textareaRect.bottom + 5 // Position slightly below the textarea
				};

				commentMentionDropdown[postId].show =
					commentMentionDropdown[postId].filteredUsers.length > 0;
				commentMentionDropdown[postId].selectedIndex = 0;

				// Force Svelte to update
				commentMentionDropdown = { ...commentMentionDropdown };
			} catch (error) {
				console.error('Error calculating dropdown position:', error);
				commentMentionDropdown[postId].show = false;
				commentMentionDropdown = { ...commentMentionDropdown };
			}
		} else {
			commentMentionDropdown[postId].show = false;
			commentMentionDropdown = { ...commentMentionDropdown };
		}
	}

	// Function to insert mention in comments
	function insertCommentMention(user, postId) {
		const textarea = commentTextareaElements[postId];
		if (!textarea) return;

		const text = newComment[postId] || '';
		const cursorPosition = textarea.selectionStart;
		const textBeforeCursor = text.substring(0, cursorPosition);
		const mentionMatch = textBeforeCursor.match(/@(\w*)$/);

		if (mentionMatch) {
			const startPos = cursorPosition - mentionMatch[0].length;
			const beforeMention = text.substring(0, startPos);
			const afterMention = text.substring(cursorPosition);

			newComment[postId] = beforeMention + `@${user.name} ` + afterMention;

			// Set cursor position after the inserted mention
			setTimeout(() => {
				textarea.focus();
				textarea.selectionStart = textarea.selectionEnd = startPos + user.name.length + 2; // +2 for '@' and space
			}, 0);
		}

		commentMentionDropdown[postId].show = false;
		commentMentionDropdown = { ...commentMentionDropdown };
	}

	// Handle keyboard navigation in the comment dropdown
	function handleCommentKeyDown(event, postId) {
		if (!commentMentionDropdown[postId]?.show) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				commentMentionDropdown[postId].selectedIndex = Math.min(
					commentMentionDropdown[postId].selectedIndex + 1,
					commentMentionDropdown[postId].filteredUsers.length - 1
				);
				commentMentionDropdown = { ...commentMentionDropdown };
				break;
			case 'ArrowUp':
				event.preventDefault();
				commentMentionDropdown[postId].selectedIndex = Math.max(
					commentMentionDropdown[postId].selectedIndex - 1,
					0
				);
				commentMentionDropdown = { ...commentMentionDropdown };
				break;

			case 'Enter':
				event.preventDefault();
				if (commentMentionDropdown[postId].filteredUsers.length > 0) {
					insertCommentMention(
						commentMentionDropdown[postId].filteredUsers[
							commentMentionDropdown[postId].selectedIndex
						],
						postId
					);
				}
				break;

			case 'Escape':
				event.preventDefault();
				commentMentionDropdown[postId].show = false;
				commentMentionDropdown = { ...commentMentionDropdown };
				break;
		}
	}

	// Function to handle mention selection
	function handleMention(event) {
		const text = event.target.value;
		const cursorPosition = event.target.selectionStart;

		// Set textareaElement reference from the event if it's not already set
		if (!textareaElement) {
			textareaElement = event.target;
		}

		// Check if we're in a potential mention context
		const textBeforeCursor = text.substring(0, cursorPosition);
		const mentionMatch = textBeforeCursor.match(/@(\w*)$/);

		if (mentionMatch && textareaElement) {
			const query = mentionMatch[1].toLowerCase();
			mentionDropdown.query = query;

			// Filter users based on query
			mentionDropdown.filteredUsers = usersList.filter((user) =>
				user.name.toLowerCase().includes(query)
			);

			// Calculate position for dropdown
			try {
				const textareaRect = textareaElement.getBoundingClientRect();
				const lineHeight = parseInt(getComputedStyle(textareaElement).lineHeight) || 20;
				const lines = textBeforeCursor.split('\n').length;

				// Position dropdown below the current line
				mentionDropdown.position = {
					left: textareaRect.left,
					top: textareaRect.top + lineHeight * lines
				};

				mentionDropdown.show = mentionDropdown.filteredUsers.length > 0;
				mentionDropdown.selectedIndex = 0;
			} catch (error) {
				console.error('Error calculating dropdown position:', error);
				mentionDropdown.show = false;
			}
		} else {
			mentionDropdown.show = false;
		}
	}

	// Function to insert the selected mention
	function insertMention(user) {
		const text = postContent;
		const cursorPosition = textareaElement.selectionStart;
		const textBeforeCursor = text.substring(0, cursorPosition);
		const mentionMatch = textBeforeCursor.match(/@(\w*)$/);

		if (mentionMatch) {
			const startPos = cursorPosition - mentionMatch[0].length;
			const beforeMention = text.substring(0, startPos);
			const afterMention = text.substring(cursorPosition);

			postContent = beforeMention + `@${user.name} ` + afterMention;

			// Set cursor position after the inserted mention
			setTimeout(() => {
				textareaElement.selectionStart = textareaElement.selectionEnd =
					startPos + user.name.length + 2; // +2 for '@' and space
			}, 0);
		}

		mentionDropdown.show = false;
	}

	// Handle keyboard navigation in the dropdown
	function handleKeyDown(event) {
		if (!mentionDropdown.show) return;

		switch (event.key) {
			case 'ArrowDown':
				event.preventDefault();
				mentionDropdown.selectedIndex = Math.min(
					mentionDropdown.selectedIndex + 1,
					mentionDropdown.filteredUsers.length - 1
				);
				break;

			case 'ArrowUp':
				event.preventDefault();
				mentionDropdown.selectedIndex = Math.max(mentionDropdown.selectedIndex - 1, 0);
				break;

			case 'Enter':
				event.preventDefault();
				if (mentionDropdown.filteredUsers.length > 0) {
					insertMention(mentionDropdown.filteredUsers[mentionDropdown.selectedIndex]);
				}
				break;

			case 'Escape':
				event.preventDefault();
				mentionDropdown.show = false;
				break;
		}
	}

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
			await fetchUsers();
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

	// Fetch all users from the API
	const fetchUsers = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/users/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok) {
				users = await response.json();
				// Filter out the logged-in user and admin users, then create a list for the dropdown
				usersList = users
					.filter((user) => user.id !== loggedInUserId && !user.is_admin)
					.map((user) => ({ value: user.id, name: user.username }));
			} else {
				console.error('Failed to fetch users');
			}
		} catch (error) {
			console.error('Network error:', error.message);
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
				// Reset the form fields
				title = '';
				postContent = '';
				selectedCommunityId = '';
				postImage = null;
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
					let token = localStorage.getItem('access_token');
					let refreshToken = localStorage.getItem('refresh_token');

					if (!token) {
						console.error('No access token found');
						postComments[postId] = [];
						// Initialize newComment for this postId
						if (!newComment[postId]) {
							newComment[postId] = '';
						}
						return;
					}

					// Try to fetch comments with the current access token
					let res = await fetch(`http://127.0.0.1:8000/comments/${postId}/`, {
						method: 'GET',
						headers: {
							Authorization: `Bearer ${token}`,
							'Content-Type': 'application/json'
						}
					});

					// If access token is expired (401), try refreshing the token
					if (res.status === 401 && refreshToken) {
						// Refresh the token
						const refreshRes = await fetch('http://127.0.0.1:8000/api/token/refresh/', {
							method: 'POST',
							headers: {
								'Content-Type': 'application/json'
							},
							body: JSON.stringify({
								refresh: refreshToken
							})
						});

						if (refreshRes.ok) {
							const data = await refreshRes.json();
							token = data.access; // Get the new access token
							// Save the new token
							localStorage.setItem('accessToken', token);

							// Retry fetching comments with the new token
							res = await fetch(`http://127.0.0.1:8000/comments/${postId}/`, {
								method: 'GET',
								headers: {
									Authorization: `Bearer ${token}`,
									'Content-Type': 'application/json'
								}
							});
						} else {
							console.error('Failed to refresh the token');
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

						// Enhance comments with user profile data
						postComments[postId] = await Promise.all(
							data.map(async (comment) => {
								// If comment user data doesn't include profile picture or full name
								if (
									!comment.user.profile_picture ||
									!comment.user.first_name ||
									!comment.user.last_name
								) {
									try {
										const profileResponse = await fetch(
											`http://127.0.0.1:8000/api/user-profile/${comment.user.user_id}/`,
											{ headers: { Authorization: `Bearer ${token}` } }
										);

										if (profileResponse.ok) {
											const profileData = await profileResponse.json();
											return {
												...comment,
												user: {
													...comment.user,
													profile_picture: profileData.profile_picture || '',
													first_name: profileData.first_name || '',
													last_name: profileData.last_name || ''
												}
											};
										}
									} catch (err) {
										console.error('Error fetching comment user profile:', err);
									}
								}
								return comment;
							})
						);

						// Initialise newComment for this postId
						if (!newComment[postId]) {
							newComment[postId] = '';
						}
					} else {
						console.error('Failed to fetch comments:', await res.text());
						postComments[postId] = [];
						// Initialize newComment for this postId
						if (!newComment[postId]) {
							newComment[postId] = '';
						}
					}
				} catch (err) {
					console.error('Error loading comments:', err);
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
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ comment: commentText })
			});

			if (response.ok) {
				const newCommentData = await response.json();

				// Enhance the comment with user profile data for immediate display
				const enhancedComment = {
					...newCommentData,
					user: {
						...newCommentData.user,
						profile_picture: userProfile.profile_picture,
						first_name: userProfile.first_name,
						last_name: userProfile.last_name
					}
				};

				// Optimistically update the UI
				postComments[postId] = [enhancedComment, ...(postComments[postId] || [])];

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
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
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

	const deleteComment = async (commentId, postId) => {
		const token = localStorage.getItem('access_token');
		if (!token) {
			console.error('No access token found.');
			return;
		}

		const confirmDelete = confirm('Are you sure you want to delete this comment?');
		if (!confirmDelete) return;

		try {
			const response = await fetch(`http://127.0.0.1:8000/api/comments/${commentId}/`, {
				method: 'DELETE',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.status === 204) {
				postComments[postId] = postComments[postId].filter((c) => c.comment_id !== commentId);
				postComments = { ...postComments };
			}
		} catch (error) {
			console.error('Error deleting comment:', error);
		}
	};

	const handleHashtagClick = (hashtag) => {
		activeHashtag = hashtag;
		filterPostsByHashtag(hashtag);
	};

	$: filteredPosts = activeHashtag
		? posts.filter((p) => p.content.toLowerCase().includes(`#${activeHashtag.toLowerCase()}`))
		: posts;

	const resetFilter = () => {
		activeHashtag = null;
		filteredPosts = allPosts;
	};

	function parseContent(content) {
		const regex = /(#(\w+)|@(\w+))/g;
		const parts = [];
		let lastIndex = 0;
		let match;

		// Iterate through the content and find all hashtags
		while ((match = regex.exec(content)) !== null) {
			// If there's text before the hashtag, add it as a text part
			if (match.index > lastIndex) {
				parts.push({ type: 'text', text: content.slice(lastIndex, match.index) });
			}
			// Determine if it's a hashtag or mention
			if (match[0].startsWith('#')) {
				parts.push({ type: 'hashtag', text: match[2] });
			} else if (match[0].startsWith('@')) {
				parts.push({ type: 'mention', text: match[3] });
			}
			lastIndex = regex.lastIndex;
		}

		if (lastIndex < content.length) {
			parts.push({ type: 'text', text: content.slice(lastIndex) });
		}

		return parts;
	}

	// Function to open user profile modal
	function openUserProfileModal(userId) {
		// Don't open modal for the current user
		if (userId === loggedInUserId) return;

		selectedUserId = userId;
		showUserProfileModal = true;
		modalLoading = true;
		modalError = false;
		modalUserProfile = null;

		console.log('Selected user ID:', selectedUserId, 'Modal visible:', showUserProfileModal);

		// Fetch user profile data
		fetchModalUserProfile(userId);
	}

	// Function to fetch user profile for modal
	async function fetchModalUserProfile(userId) {
		try {
			const token = localStorage.getItem('access_token');
			if (!token) {
				throw new Error('No access token found');
			}

			const response = await fetch(`http://127.0.0.1:8000/api/user-profile/${userId}/`, {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				throw new Error('Failed to fetch user profile');
			}

			modalUserProfile = await response.json();
			console.log('Fetched modal user profile:', modalUserProfile);
		} catch (err) {
			console.error('Error fetching user profile:', err);
			modalError = true;
		} finally {
			modalLoading = false;
		}
	}

	// Function to close the modal
	function closeUserProfileModal() {
		console.log('Closing modal');
		showUserProfileModal = false;
		selectedUserId = null;
	}

	// Function to handle clicking outside the modal
	function handleModalClickOutside(event) {
		const modalContent = document.getElementById('user-profile-modal-content');
		if (modalContent && !modalContent.contains(event.target)) {
			closeUserProfileModal();
		}
	}
</script>

<main class="px-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>

	{#if activeHashtag}
		<div class="alert alert-info mb-4">
			<span>Filtering by hashtag: <strong>#{activeHashtag}</strong></span>
			<button class="btn btn-sm" on:click={resetFilter}>Reset Filter</button>
		</div>
	{/if}

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
								on:input={(e) => {
									adjustTextareaHeight(e);
									handleMention(e);
								}}
								on:keydown={handleKeyDown}
							></textarea>
							{#if mentionDropdown.show}
								<div
									class="z-50 bg-secondary rounded-md shadow-lg max-h-48 overflow-y-auto"
									style="top: {mentionDropdown.position.top}px; left: {mentionDropdown.position
										.left}px; min-width: 200px;"
								>
									<ul class="py-1">
										{#each mentionDropdown.filteredUsers as user, index}
											<li
												class="px-4 py-2 hover:bg-primary hover:text-secondary cursor-pointer {index ===
												mentionDropdown.selectedIndex
													? 'bg-primary text-secondary'
													: ''}"
												on:click={() => insertMention(user)}
											>
												@{user.name}
											</li>
										{/each}
									</ul>
								</div>
							{/if}
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
		<div class="card bg-base-100 w-full rounded-3xl mb-5">
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
							class="profile-picture cursor-pointer"
							on:click={() =>
								p.user_id === loggedInUserId ? goto('/profile') : openUserProfileModal(p.user_id)}
						/>
					{:else}
						<div
							class="cursor-pointer"
							on:click={() =>
								p.user_id === loggedInUserId ? goto('/profile') : openUserProfileModal(p.user_id)}
						>
							<ProfilePictureIcon size={50} class="profile-picture" />
						</div>
					{/if}
					<div class="ml-2 mt-0 flex flex-col">
						<p class="text-base-100 text-lg font-bold">
							<span
								class="cursor-pointer hover:underline"
								on:click={() =>
									p.user_id === loggedInUserId ? goto('/profile') : openUserProfileModal(p.user_id)}
							>
								{p.userProfile.first_name}
								{p.userProfile.last_name}
							</span>
							<span class="font-normal cursor-pointer">
								@{p.userProfile.username}
							</span>
							<span class="font-normal">· {formatDate(p.date)}</span>
						</p>
						<h3 class="text-primary text-lg font-bold">{p.title}</h3>
						<p class="text-base-100 overflow-auto text-ellipsis" style="word-break: break-word;">
							<!-- {p.content} -->
							{#each parseContent(p.content) as part}
								{#if part.type === 'hashtag'}
									<span
										style="color: #3b82f6; cursor: pointer;"
										on:click={() => handleHashtagClick(part.text)}
									>
										#{part.text}
									</span>
								{:else if part.type === 'mention'}
									<span
										style="color: #3b82f6; cursor: pointer;"
										on:click={() => {
											const user = usersList.find((u) => u.name === part.text);
											if (user) {
												openUserProfileModal(user.value);
											} else if (part.text === userProfile.username) {
												goto('/profile');
											}
										}}
									>
										@{part.text}
									</span>
								{:else}
									{part.text}
								{/if}
							{/each}
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

				<!-- Like and comment section -->
				<div class="flex items-center gap-x-4">
					<button class="flex items-center gap-x-1" on:click={() => likeUnlikePost(p.id)}>
						{#if p.user_liked}
							<LikedIcon />
						{:else}
							<LikeIcon />
						{/if}
						<p>{p.like_count !== undefined ? p.like_count : 0} Likes</p>
					</button>
					<div
						class="flex items-center gap-x-1 cursor-pointer"
						on:click={() => toggleComments(p.id)}
					>
						<CommentIcon />
						<p>{p.comment_count !== undefined ? p.comment_count : 'View'} Comments</p>
					</div>
				</div>
				<!-- Comments section -->
				{#if activeCommentPostId === p.id}
					<div class="mt-4 bg-base-200 p-4 rounded-xl">
						{#if loadingComments}
							<p class="italic">Loading comments...</p>
						{:else}
							<!-- Comment Input Area with Profile Picture -->
							<div class="mb-4 flex items-start gap-3">
								{#if userProfile.profile_picture}
									<img
										src={`data:image/jpeg;base64,${userProfile.profile_picture}`}
										alt="Your Profile"
										class="w-10 h-10 rounded-full object-cover"
									/>
								{:else}
									<ProfilePictureIcon size={40} class="rounded-full" />
								{/if}
								<div class="flex-1 relative">
									<textarea
										placeholder={postComments[p.id]?.length
											? 'Add a comment...'
											: 'Be the first to comment on this post!'}
										class="input input-bordered text-area-input w-full mb-3 min-h-[60px]"
										bind:value={newComment[p.id]}
										on:input={(e) => handleCommentMention(e, p.id)}
										on:keydown={(e) => handleCommentKeyDown(e, p.id)}
									></textarea>

									{#if commentMentionDropdown[p.id]?.show}
										<div
											class="z-50 bg-secondary rounded-md shadow-lg max-h-48 overflow-y-auto"
											style="top: {commentMentionDropdown[p.id].position
												.top}px; left: {commentMentionDropdown[p.id].position
												.left}px; min-width: 200px;"
										>
											<ul class="py-1">
												{#each commentMentionDropdown[p.id].filteredUsers as user, index}
													<li
														class="px-4 py-2 hover:bg-primary hover:text-secondary cursor-pointer {index ===
														commentMentionDropdown[p.id].selectedIndex
															? 'bg-primary text-secondary'
															: ''}"
														on:click={() => insertCommentMention(user, p.id)}
													>
														@{user.name}
													</li>
												{/each}
											</ul>
										</div>
									{/if}

									<button
										class="btn btn-primary text-secondary hover:bg-primary-focus w-auto btn-sm"
										on:click={() => postComment(p.id)}
									>
										Comment
									</button>
								</div>
							</div>

							<!-- Comments List -->
							{#if postComments[p.id]?.length}
								<div class="space-y-3">
									{#each postComments[p.id] as c}
										<div class="flex items-start gap-3">
											<!-- Comment User Profile Picture -->
											{#if c.user?.profile_picture}
												<img
													src={`data:image/jpeg;base64,${c.user.profile_picture}`}
													alt="{c.user.username}'s profile"
													class="w-10 h-10 rounded-full object-cover cursor-pointer"
													on:click={() =>
														c.user.user_id === loggedInUserId
															? goto('/profile')
															: openUserProfileModal(c.user.user_id)}
												/>
											{:else}
												<div
													class="cursor-pointer"
													on:click={() =>
														c.user.user_id === loggedInUserId
															? goto('/profile')
															: openUserProfileModal(c.user.user_id)}
												>
													<ProfilePictureIcon size={40} class="rounded-full" />
												</div>
											{/if}

											<!-- Comment Content -->
											<div class="flex-1 bg-secondary rounded-xl">
												<div class="flex justify-between items-start">
													<div>
														<span
															class="font-bold text-base-content cursor-pointer hover:underline"
															on:click={() =>
																c.user.user_id === loggedInUserId
																	? goto('/profile')
																	: openUserProfileModal(c.user.user_id)}
														>
															{c.user?.first_name}
															{c.user?.last_name}
														</span>
														<span class="text-gray-500 text-sm ml-1">
															@{c.user.username}
														</span>
														<span class="text-gray-500 text-xs ml-2"
															>· {formatDate(c.timestamp)}</span
														>
													</div>

													<!-- Delete button if user's own comment -->
													{#if loggedInUserId === c.user.user_id}
														<button
															class="text-gray-500 hover:text-red-500"
															on:click={() => deleteComment(c.comment_id, p.id)}
														>
															<BinIcon size={16} />
														</button>
													{/if}
												</div>
												<!-- Parse and highlight mentions in the comment -->
												<p class="text-base-content mt-1">
													{#each parseContent(c.comment) as part}
														{#if part.type === 'hashtag'}
															<span
																style="color: #3b82f6; cursor: pointer;"
																on:click={() => handleHashtagClick(part.text)}
															>
																#{part.text}
															</span>
														{:else if part.type === 'mention'}
															<span
																style="color: #3b82f6; cursor: pointer;"
																on:click={() => {
																	const user = usersList.find((u) => u.name === part.text);
																	if (user) {
																		openUserProfileModal(user.value);
																	} else if (part.text === userProfile.username) {
																		goto('/profile');
																	}
																}}
															>
																@{part.text}
															</span>
														{:else}
															{part.text}
														{/if}
													{/each}
												</p>
											</div>
										</div>
									{/each}
								</div>
							{/if}
						{/if}
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

	{#if showUserProfileModal}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-100"
			on:click={handleModalClickOutside}
		>
			<div
				id="user-profile-modal-content"
				class="bg-secondary rounded-3xl p-13 max-w-lg min-w-[40%] w-full max-h-[90vh] overflow-y-auto"
				on:click|stopPropagation
			>
				<!-- Close button -->
				<button
					class="absolute top-4 right-4 text-primary hover:text-base-100"
					on:click={closeUserProfileModal}
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>

				{#if modalLoading}
					<div class="flex justify-center items-center h-64">
						<span class="loading loading-spinner loading-lg text-primary"></span>
					</div>
				{:else if modalError}
					<div class="text-center p-8">
						<p class="text-red-500">Failed to load user profile.</p>
					</div>
				{:else if modalUserProfile}
					<div class="flex flex-col items-center">
						<!-- Center the profile picture -->
						<div class="w-50 h-50 mb-6">
							{#if modalUserProfile.profile_picture}
								<img
									src={`data:image/jpeg;base64,${modalUserProfile.profile_picture}`}
									alt="Profile Picture"
									class="h-full w-full object-cover rounded-full"
								/>
							{:else}
								<ProfilePictureIcon size={200} class="h-full w-full object-cover rounded-full" />
							{/if}
						</div>
					</div>

					<div class="flex items-center gap-2">
						<span class="text-3xl font-bold">
							{modalUserProfile.first_name || ''}
							{modalUserProfile.last_name || ''}
						</span>

						<span class="text-2xl font-normal text-gray-400">
							@{modalUserProfile.username}
						</span>
					</div>

					<!-- User Information -->
					<div class="space-y-6">
						{#if modalUserProfile.uni_year || modalUserProfile.program}
							<div class="flex items-center gap-2">
								<p>
									{modalUserProfile.program || 'Not specified'}
									{#if modalUserProfile.uni_year}
										- Year {modalUserProfile.uni_year}
									{/if}
								</p>
							</div>
						{:else}
							<!-- This empty div maintains spacing even when there's no education info -->
							<div class="h-4"></div>
						{/if}

						{#if modalUserProfile.about}
							<div>
								<h3 class="text-xl font-semibold text-primary mb-2">About</h3>
								<p class="text-lg">{modalUserProfile.about}</p>
							</div>
						{/if}

						{#if modalUserProfile.social_links && modalUserProfile.social_links.length > 0}
							<div>
								<h3 class="text-xl font-semibold text-primary mb-2">Social Media</h3>
								<div class="flex flex-wrap gap-2">
									<!-- Loop through social media accounts -->
									{#each modalUserProfile.social_links as link}
										{#each socialMedias as social (social.name)}
											{#if social.name === link.social_type}
												<div class="badge-outline badge p-3 flex items-center gap-2">
													<div class="w-5 h-5 flex items-center justify-center">
														{@html social.svg}
													</div>
													<p class="text-lg">{link.social_username}</p>
												</div>
											{/if}
										{/each}
									{/each}
								</div>
							</div>
						{/if}

						{#if modalUserProfile.interests && modalUserProfile.interests.length > 0}
							<div>
								<h3 class="text-xl font-semibold text-primary mb-2">Interests</h3>
								<div class="flex flex-wrap gap-2">
									{#each modalUserProfile.interests as interest}
										<span class="badge badge-outline text-lg">{interest}</span>
									{/each}
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<div class="text-center p-8">
						<p>No profile data available</p>
					</div>
				{/if}
			</div>
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
