<script>
	import { CATEGORIES } from '../../assets/categories.json';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { MultiSelect, Badge } from 'flowbite-svelte';

	let access_token;
	let name = '';
	let description = '';
	let category = '';
	let customCategory = '';
	let users = []; // List of users fetched from the API
	let selectedUsers = [];
	let usersList = []; // List of users for the MultiSelect component
	let message = '';
	let loggedInUserId; // ID of the logged-in user to avoid adding them as a community leader, they are automatically added as the owner
	let communities = [];
	let subscribedCommunities = [];

	// Sort the categories alphabetically
	let categories = [...CATEGORIES.sort((a, b) => a.trim().localeCompare(b.trim())), 'Other'];

	onMount(() => {
		// Get the access token from localStorage
		access_token = localStorage.getItem('access_token');

		// If no token, redirect to login
		if (!access_token) {
			window.location.href = '/login'; // You can use Svelte's `goto()` if you have it imported
		} else {
			// Fetch communities when the page loads
			fetch_your_communities();
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

	onMount(async () => {
		// Retrieve the access_token from localStorage
		access_token = localStorage.getItem('access_token');

		// If there's no access_token, redirect to the login page or home
		if (!access_token) {
			goto('http://localhost:5173/'); // Or wherever you want the user to go if they are not logged in
		} else {
			loggedInUserId = getLoggedInUserIdFromToken(access_token);

			// Fetch users and subscribed communities on page load.
			await fetchUsers();
			await fetchSubscribedCommunities();
		}
	});

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

	let your_communities = [];

	const fetch_communities = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/communities/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (response.ok) {
				communities = await response.json();
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};

	// Fetch your communities
	const fetch_your_communities = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/your_communities/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok) {
				const data = await response.json();
				console.log('Fetched Your Communities:', data);
				your_communities = data; // This will trigger reactivity in Svelte
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};

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
			leader_ids: selectedUsers
		};
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
				//window.location.reload();
				console.log('Community created:', result);
				message = 'Community created successfully!';
				name = '';
				description = '';
				category = '';
				selectedUsers = [];
				window.location.reload();
			} else {
				console.error('Error creating community:', result.error || 'Something went wrong');
				message = 'Failed to create community!';
			}
		} catch (error) {
			console.error('Network Error:', error.message);
			message = 'An error occurred. Please try again!';
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
				await fetch_your_communities();
			} else {
				console.error(result.error);
			}
		} catch (error) {
			console.error('Error joining community:', error);
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
				await fetch_your_communities();
			} else {
				console.error(result.error);
			}
		} catch (error) {
			console.error('Error leaving community:', error);
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
										placeholder="Enter your community name"
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
									<input
										type="text"
										id="description"
										bind:value={description}
										required
										class="input input-bordered validator custom-input"
										placeholder="Enter a description for your community"
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
										class="input input-bordered validator custom-input placeholder-selected outline-base-100 border-base-100"
										on:change={updateSelectClass}
									>
										<option value="" disabled selected style="color: var(--color-primary);"
											>Select a category</option
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
											placeholder="Enter your custom category"
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
										bind:value={selectedUsers}
										placeholder="Select community leaders"
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
						<div class="form-control text-primary flex justify-center pt-2 text-center">
							{#if message}
								<p>{message}</p>
							{:else}
								<p class="invisible flex">PlaceholderPlaceholderPlaceholder</p>
							{/if}
						</div>
						<div class="form-control mb-2 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-1/5"
								type="submit">Create</button
							>
						</div>
					</form>
				</div>
			</div>
		</div>

		<!-- Right Column -->
		<div class="space-y-10">
			<!-- Socials Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">User created communities</h1>
						</div>
					</div>
					<div class="flex flex-wrap justify-center space-y-2">
						<!-- Your Community Card -->
						<!-- TODO: We need to change this to user's created communities or if they are community leaders, we can subscribe them automatically? -->

						<form id="community-form" on:submit={submitForm}>
							<!-- Form content goes here, similar to what you already have -->
						</form>

						<!-- List Communities and Join Button -->
						<div class="flex flex-wrap justify-center gap-4">
							{#each communities as community}
								<div
									class="flex items-center bg-base-200 px-6 py-3 rounded-lg shadow-md border border-gray-300"
								>
									<p class="text-lg font-semibold text-gray-800 pr-3">{community.name}</p>

									<!-- Check if the user is neither the owner nor the leader before showing the Join button -->
									{#if !community.is_owner && !community.is_leader}
										<button
											on:click={() => join_community(community.community_id)}
											class="btn btn-accent px-4 py-2 text-white rounded-lg font-medium shadow hover:bg-accent-focus"
										>
											Join
										</button>
									{/if}
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		</div>
		<div class="space-y-10">
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<h1 class="text-primary text-4xl font-bold text-center">Your Communities</h1>
					<div class="flex flex-wrap justify-center space-x-2 space-y-2">
						<form id="community-form" on:submit={submitForm}>
							<!-- Form content goes here, similar to what you already have -->
						</form>
						{#each your_communities as community}
							<div class="border-base-100 m-1 flex items-center space-x-2 rounded-lg border-2 p-2">
								<p class="text-user-details pr-2">{community.name}</p>
								<!-- Show "Leave" button for users who are members -->
								{#if community.is_owner || community.is_leader}
									<button
										on:click={() => leave_community(community.community_id)}
										class="bg-red-500 text-white px-4 py-2 rounded-lg"
									>
										X
									</button>
								{/if}
							</div>
						{/each}
						{#each subscribedCommunities as community}
							<div>
								{community.name}
								{community.description}
								{community.category}
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>
	</div>
</main>
