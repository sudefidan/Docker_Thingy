<script>
	import { CATEGORIES } from '../../assets/categories.json';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { MultiSelect, Badge } from 'flowbite-svelte';

	let categories = [...CATEGORIES.sort((a, b) => a.trim().localeCompare(b.trim())), 'Other']; // Sort the categories alphabetically

	let access_token;
	let name = ''; // Community name
	let description = ''; // Community description
	let category = ''; // Community category
	let customCategory = ''; // Custom category if category is 'Other'
	let users = []; // List of users fetched from the API
	let selectedUsersForCommunityCreation = []; // Selected users to be Community Leaders
	let usersList = []; // List of users for the MultiSelect component
	let managementMessage = ''; // Success or error message for community management
	let loggedInUserId; // ID of the logged-in user to avoid adding them as a community leader, they are automatically added as the owner
	let communities = []; // List of all the communities fetched from the API
	let subscribedCommunities = []; // List of communities the user is subscribed to
	$: community_management_selected = null; // The selected community for management
	let new_community_name = null; // New name for the community
	let new_community_description = null; // New description for the community
	let new_community_category = null; // New category for the community
	$: community_leaders = []; // Current members of the selected community
	let community_member_to_demote = null; // Member to demote from leader
	let community_member_to_promote = null; // Member to promote to leader
	let selectedAction = ''; // Variable to store the selected action

	// Function to adjust the height of the textarea dynamically
	function adjustTextareaHeight(event) {
		const textarea = event.target;
		textarea.style.height = 'auto'; // Reset the height
		textarea.style.height = `${textarea.scrollHeight}px`; // Set the height to the scroll height
	}

	// Function to handle action change for community management commands
	function handleActionChange(event) {
		selectedAction = event.target.value;
	}

	onMount(async () => {
		// Retrieve the access_token from localStorage
		access_token = localStorage.getItem('access_token');

		// If there's no access_token, redirect to the login page or home
		if (!access_token) {
			goto('http://localhost:5173/'); // Or wherever you want the user to go if they are not logged in
		} else {
			loggedInUserId = getLoggedInUserIdFromToken(access_token);
			await fetchUsers(); // Fetch users from the API
			await fetchSubscribedCommunities(); // Fetch subscribed communities
		}
	});

	// Placeholder color for option
	function updateSelectClass(event) {
		const selectElement = event.target;
		if (selectElement.value === '') {
			selectElement.classList.add('placeholder-selected');
		} else {
			selectElement.classList.remove('placeholder-selected');
		}
	}

	// fetches the subscribed communities that the current user is subscribed too
	const fetchSubscribedCommunities = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/subscribed_communities/', {
				method: 'GET',
				headers: { Authorization: `Bearer ${access_token}` }
			});

			if (response.ok) {
				const data = await response.json();
				subscribedCommunities = data.subscribed_communities;
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

	// Fetch users from the API
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
				// Filter out the logged-in user and create a list of users for the MultiSelect component
				usersList = users
					.filter((user) => user.id !== loggedInUserId)
					.map((user) => ({ value: user.id, name: user.username }));
			} else {
				console.error('Failed to fetch users');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};

	onMount(async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/communities/');
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			const data = await response.json();
			communities = data;
		} catch (error) {
			console.error('Error fetching communities:', error);
		}
	});

	// submit form to create a new community
	const submitForm = async (event) => {
		event.preventDefault();
		// checks if all fields are completed if not it will not submit
		if (!name || !description || !category) {
			console.log('All fields are required!');
			return;
		}
		// data that will be passed through the api
		const data = {
			name,
			description,
			category: category === 'Other' ? customCategory : category,
			leader_ids: selectedUsersForCommunityCreation
		};

		const confirmation = confirm('Are you sure?');
		if (!confirmation) return;


		// the api call and post method
		try {
			const response = await fetch('http://127.0.0.1:8000/api/create_community/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${access_token}`
				},
				body: JSON.stringify(data)
			});

			const result = await response.json();
			// if it worked and is okay display in the console log the data passed through and then reload the window
			if (response.ok) {
				console.log('Community created:', result);
				name = '';
				description = '';
				category = '';
				selectedUsersForCommunityCreation = [];
				window.location.reload();
			} else {
				alert(result.error);
				console.error('Error creating community:', result.error || 'Something went wrong');
			}
		} catch (error) {
			console.error('Network Error:', error.message);
			alert('An error occurred. Please try again!');
		}
	};

	const join_community = async (communityId) => {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/join_community/${communityId}/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${access_token}`
				}
			});

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				alert('You have successfully joined the community!');
				await fetchSubscribedCommunities();
			} else {
				console.error(result.error);
			}
		} catch (error) {
			console.error('Error joining community:', error);
			alert('An error occurred while joining the community.');
		}
	};

	const leave_community = async (communityId) => {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/leave_community/`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${access_token}`
				}
			});

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				alert('You have successfully left the community!');
				await fetch_your_communities();
			} else {
				console.error(result.error);
			}
		} catch (error) {
			console.error('Error leaving community:', error);
			alert('An error occurred while leaving the community.');
		}
	};

	const submit_community_management = async (type, value) => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/communities/update_community_${type}/`,
				{
					method: 'PUT',
					headers: {
						Authorization: `Bearer ${access_token}`,
						'Content-Type': 'application/json'
					},
					body: JSON.stringify({
						value,
						community_id: community_management_selected
					})
				}
			);

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				location.reload();
			} else {
				console.error(result.error);
			}
		} catch (error) {
			console.error('Error changing community settings: ', error);
		}
	};

	const delete_community = async () => {
		if (!community_management_selected) {
			console.error('No community selected for deletion.');
			managementMessage = 'Select a community to delete.';
			return;
		}

		const confirmation = confirm('Are you sure? This cannot be undone.');
		if (!confirmation) return;

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/communities/delete/${community_management_selected}`,
				{
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				location.reload(); // Refresh the page to reflect the deletion
			} else {
				console.error(result.error);
				alert(result.error); // Show the error to the user
			}
		} catch (error) {
			console.error('Error deleting community:', error);
			alert('An error occurred while deleting the community.');
		}
	};

	// Function to demote a community leader
	const delete_community_leader = async () => {
		if (!community_management_selected) {
			console.error('No community selected for deletion.');
			return;
		}

		if (!community_member_to_demote) {
			console.error('No member selected.');
			return;
		}

		const confirmation = confirm('Are you sure? This cannot be undone.');
		if (!confirmation) return;

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/community/${community_management_selected}/leaders/${community_member_to_demote}/delete/`,
				{
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				location.reload(); // Refresh the page to reflect the deletion
			} else {
				console.error(result.error);
				alert(result.error); // Show the error to the user
			}
		} catch (error) {
			console.error('Error demoting community leader:', error);
			alert('An error occurred while demoting the community leader.');
		}
	};

	// Function to promote a user to community leader
	const add_community_leader = async () => {
		if (!community_management_selected) {
			console.error('No community selected for deletion.');
			return;
		}

		if (!community_member_to_promote) {
			console.error('No member selected.');
			return;
		}

		const confirmation = confirm('Are you sure?');
		if (!confirmation) return;

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/community/${community_management_selected}/leaders/${community_member_to_promote}/add/`,
				{
					method: 'POST',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);

			const result = await response.json();
			if (response.ok) {
				console.log(result.message);
				location.reload(); // Refresh the page to reflect the deletion
			} else {
				console.error(result.error);
				alert(result.error); // Show the error to the user
			}
		} catch (error) {
			console.error('Error adding community leader:', error);
			alert('An error occurred while adding the community leader.');
		}
	};

	// Function to fetch community leaders
	const get_community_leaders = async () => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/community/get_leaders/${community_management_selected}`,
				{
					method: 'GET',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);
			if (response.ok) {
				const data = await response.json();
				community_leaders = data;
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};
</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<div
		class="gap-13 flex grid w-full max-w-full grid-cols-1 flex-col justify-center md:grid-cols-2"
	>
		<!-- Left Column -->
		<div class="space-y-10">
			<div class="card bg-base-100 min-h-1/2 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">Create Community</h1>
					<form id="community-form" class="space-y-4" on:submit={submitForm}>
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="name" class="label">
									<span class="label-text">Name</span>
								</label>
								<div class="relative">
									<input
										type="text"
										id="name"
										bind:value={name}
										required
										class="input input-bordered validator custom-input"
										placeholder="What's your community's name?"
									/>
								</div>
							</div>
						</div>

						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="description" class="label">
									<span class="label-text">Description</span>
								</label>
								<div class="relative">
									<textarea
										id="description"
										bind:value={description}
										required
										class="input input-bordered text-area-input"
										placeholder="What's your community's description?"
										on:input={adjustTextareaHeight}
									/>
								</div>
							</div>
						</div>
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="category" class="label">
									<span class="label-text">Category</span>
								</label>
								<div class="relative">
									<select
										id="category"
										bind:value={category}
										required
										class="select select-bordered validator custom-input placeholder-selected outline-base-100 border-base-100"
										on:change={updateSelectClass}
									>
										<option value="" disabled selected style="color: var(--color-primary);"
											>Which category suits your community?</option
										>
										{#each categories as category}
											<option value={category}>{category}</option>
										{/each}
									</select>
								</div>
							</div>
						</div>
						{#if category === 'Other'}
							<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
								<div class="w-full">
									<div class="relative">
										<input
											type="text"
											id="customCategory"
											bind:value={customCategory}
											required
											class="input input-bordered validator custom-input"
											placeholder="Got a category in mind?"
										/>
									</div>
								</div>
							</div>
						{/if}
						<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="name" class="label">
									<span class="label-text">Community Leaders(Optional)</span>
								</label>
								<div class="relative">
									<MultiSelect
										items={usersList}
										underline="true"
										bind:value={selectedUsersForCommunityCreation}
										placeholder="Who are the leaders of your community?"
										class="border-base-100 custom-input ring-transparent"
										dropdownClass="bg-secondary"
										let:item
										let:clear
									>
										<Badge
											class="border"
											dismissable
											style="border-color: var(--color-accent);"
											params={{ duration: 100 }}
											on:close={clear}
										>
											{item.name}
										</Badge>
									</MultiSelect>
								</div>
							</div>
						</div>

						<div class="form-control mb-2 mt-6 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								type="submit">Create</button
							>
						</div>
					</form>
				</div>
			</div>
		</div>
	</div>
</main>
