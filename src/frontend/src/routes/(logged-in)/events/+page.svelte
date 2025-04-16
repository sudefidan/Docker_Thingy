<script>
	import { onMount } from 'svelte';

	let access_token;
	let loggedInUserId = null;
	let users = []; // List of users fetched from API
	let communities = []; // Stores the user's owned/managed communities
	let allowedToCreate = false; // Controls form visibility
	let title = '';
	let description = '';
	let date = '';
	let virtual_link = '';
	let location = '';
	let event_type = 'virtual';
	let community_id = ''; // This is where the selected community will be stored
	let searchTerm = '';
	let events = [];
	// Search term for filtering

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

	// Fetch user communities
	async function fetchUserCommunities() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/user/communities/', {
				headers: {
					Authorization: `Bearer ${access_token}`,
				}
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch communities: ${response.status}`);
			}

			const data = await response.json();
			console.log('API Response for user communities:', data); // Log the full response

			// Check if the response is an array
			if (Array.isArray(data)) {
				communities = data; // Directly assign the array to 'communities'
				allowedToCreate = communities.length > 0;
			} else {
				console.error('Communities data is not an array');
			}

		} catch (error) {
			console.error('Error fetching user communities:', error);
		}
	}

	// Submit event form
	async function submitEvent(event) {
		event.preventDefault(); // Prevent default form submission

		console.log("Form submission triggered.");

		const eventData = {
			title,              
			description,
			date,
			virtual_link: virtual_link === "" ? null : virtual_link,  
			location,
			event_type,          
			community_id         
		};

		// Log event data, including community_id
		console.log("Event Data:", eventData);

		try {
			console.log("Sending POST request to API...");

			const response = await fetch('http://127.0.0.1:8000/api/events/create', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`, 
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(eventData),
			});

			console.log("Response Status:", response.status);

			if (!response.ok) {
				throw new Error(`Failed to create event: ${response.status}`);
			}

			const data = await response.json();

			console.log('Event created successfully:', data);


		} catch (error) {
			console.error('Error creating event:', error);
		}
	}

	// Fetch events
	async function fetchEvents() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/events/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`,  
				}
			});

			if (!response.ok) {
				throw new Error('Failed to fetch events');
			}

			events = await response.json();
			console.log('Fetched events:', events);

		} catch (error) {
			console.error('Error fetching events:', error);
		}
	}

	// Run the functions when the component loads
	onMount(async () => {
		try {
			access_token = localStorage.getItem('access_token');
			if (!access_token) {
				goto('http://localhost:5173/');
				return;
			}

			loggedInUserId = getLoggedInUserIdFromToken(access_token);

			await fetchUsers();
			await fetchUserCommunities();
			await fetchEvents();
			const response = await fetch('http://127.0.0.1:8000/api/communities/', {
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			const allCommunities = await response.json();

			const permitted = [];
			console.log("Communities:", communities);

			// Check each community to see if user is owner or leader
			for (const community of allCommunities) {
				const isOwner = community.owner_id === loggedInUserId;

				// Get leaders for this community
				const leadersResponse = await fetch(
					`http://127.0.0.1:8000/api/community/get_leaders/${community.community_id}`,
					{
						headers: {
							Authorization: `Bearer ${access_token}`
						}
					}
				);
				if (!leadersResponse.ok) {
					console.error(`Failed to get leaders for community ${community.community_id}`);
					continue;
				}
				const leaders = await leadersResponse.json();
				const isLeader = leaders.some((leader) => leader.id === loggedInUserId);

				if (isOwner || isLeader) {
					permitted.push(community);
				}
			}

			communities = permitted;
			allowedToCreate = permitted.length > 0;
		} catch (error) {
			console.error('Error during initialization:', error);
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
									<option value={community.community_id}>{community.name}</option>
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
	<!-- Events List -->
	<div class="card bg-base-100 w-full rounded-3xl mt-5">
		<div class="card-body bg-secondary rounded-3xl">
			<h2>Your Events</h2>
			{#if events.length === 0}
				<p>No events available.</p>
			{:else}
				<div class="events-list">
					{#each events as event}
						<div class="event-card">
							<h3>{event.title}</h3>
							<p>{event.description}</p>
							<p><strong>Date:</strong> {event.date}</p>
							<p><strong>Event Type:</strong> {event.event_type}</p>
							<p><strong>Location:</strong> {event.location || 'Online'}</p>
							{#if event.virtual_link}
								<p><strong>Virtual Link:</strong> <a href={event.virtual_link} target="_blank">Join Event</a></p>
							{/if}
							<p><strong>Community:</strong> {event.community}</p>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</main>
