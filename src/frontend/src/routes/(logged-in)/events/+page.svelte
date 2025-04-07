<script>
	import { onMount } from 'svelte';

	let access_token;
	let loggedInUserId = null;
	let users = []; // List of users fetched from API
	let usersList = []; // List of users for MultiSelect component
	let communities = []; // Stores the user's owned/managed communities
	let allowedToCreate = false; // Controls form visibility
	let submitEvent = '';
	let title = '';
	let description = '';
	let date = '';
	let virtual_link = '';
	let location = '';
	let event_type = 'virtual';
	let community_id = '';
	let searchTerm = ''; // Search term for filtering

	// Retrieve the logged-in user's ID from the JWT token
	function getLoggedInUserIdFromToken(token) {
		try {
			const payload = JSON.parse(atob(token.split('.')[1])); // Decode JWT payload
			return payload.user_id;
		} catch (error) {
			console.error('Invalid token:', error);
			return null;
		}
	}

	// Fetch the list of users
	async function fetchUsers() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/users/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`, // Add token
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				throw new Error(`Failed to fetch users: ${response.status}`);
			}

			const data = await response.json();
			users = data.filter((user) => user.id !== loggedInUserId);
		} catch (error) {
			console.error('Error fetching users:', error);
		}
	}

	// Fetch communities where the user is an owner or leader
	async function fetchAllowedCommunities() {
		try {
			// Retrieve access token from localStorage
			const access_token = localStorage.getItem('access_token');
			if (!access_token) {
				console.error('No access token found! Redirecting...');
				window.location.href = '/'; // Redirect if not authenticated
				return;
			}

			const response = await fetch('http://127.0.0.1:8000/api/fetch_owned_communities/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`, // Add token
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				if (response.status === 401) {
					console.error('Unauthorized! Token might be invalid or expired.');
					window.location.href = '/'; // Redirect if token expired
				}
				throw new Error(`Failed to fetch communities: ${response.status}`);
			}

			const data = await response.json();
			communities = data; // Store the fetched communities

			// Check if user owns or leads at least one community
			allowedToCreate = communities.length > 0;
		} catch (error) {
			console.error('Error fetching communities:', error);
		}
	}

	// Run the function when the component loads
	onMount(fetchAllowedCommunities);

	// Run the functions when the component loads
	onMount(() => {
		access_token = localStorage.getItem('access_token');

		if (!access_token) {
			console.error('No access token found! Redirecting...');
			window.location.href = '/'; // Redirect to login
		} else {
			loggedInUserId = getLoggedInUserIdFromToken(access_token);
			fetchUsers();
			fetchAllowedCommunities();
		}
	});
</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<!-- Top panel with search bar -->
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>
	<div class="card bg-base-100 w-full rounded-3xl">
		<div class="card-body bg-secondary rounded-3xl">
			{#if allowedToCreate}
				<!-- Your form fields here -->
				<form on:submit={submitEvent} id="createEventForm" class="form-container">
					<div class="form-group">
						<label for="title">Title:</label>
						<input type="text" bind:value={title} id="title" class="form-input" required />
					</div>

					<div class="form-group">
						<label for="description">Description:</label>
						<textarea bind:value={description} id="description" class="form-input" required
						></textarea>
					</div>

					<div class="form-group">
						<label for="date">Date:</label>
						<input type="date" bind:value={date} id="date" class="form-input" required />
					</div>

					<div class="form-group">
						<label for="virtual_link">Virtual Link:</label>
						<input type="url" bind:value={virtual_link} id="virtual_link" class="form-input" />
					</div>

					<div class="form-group">
						<label for="location">Location:</label>
						<input type="text" bind:value={location} id="location" class="form-input" />
					</div>

					<div class="form-group">
						<label for="event_type">Event Type:</label>
						<select bind:value={event_type} id="event_type" class="form-input" required>
							<option value="virtual">Virtual</option>
							<option value="in-person">In-Person</option>
						</select>
					</div>

					<div class="form-group">
						<label for="community">Community:</label>
						<select bind:value={community_id} id="community" class="form-input" required>
							<option value="" disabled selected>-- Choose a community --</option>
							{#if communities.length === 0}
								<option disabled>No communities found</option>
							{:else}
								{#each communities as community}
									<option value={community.id}>{community.name}</option>
								{/each}
							{/if}
						</select>
					</div>

					<button type="submit" class="submit-btn">Create Event</button>
				</form>
			{:else}
				<p>You do not have permission to create events.</p>
			{/if}
		</div>
	</div>
</main>
