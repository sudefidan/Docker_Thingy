<script>
	import { onMount } from 'svelte';
	import AddIconNoCircle from '../../../assets/AddIconNoCircle.svelte';

	let access_token;
	let loggedInUserId = null;
	let users = []; // List of users fetched from API
	let managedEvents = [];
	let communities = []; // Stores the user's owned/managed communities
	let allowedToCreate = false; // Controls form visibility
	let title = '';
	let description = '';
	let date = '';
	let virtualLinkInput = '';
	let locationInput = '';
	let event_type = '';
	let community_id = ''; // This is where the selected community will be stored
	let searchTerm = ''; // Search term for filtering events
	let events = []; // List of events fetched from API
	let showEventModal = false; // Controls the visibility of the event modal

	// Edit Event Form State
	let editEventId = null; // Still useful to know which event we're editing
	let editTitle = '';
	let editDescription = '';
	let editDate = '';
	let editVirtualLink = '';
	let editLocation = '';
	let editEventType = '';
	let selectedEventEditCategory = '';
	let allowedToEdit = false;

	// Function to toggle the post creation modal
	const toggleEventModal = () => {
		showEventModal = !showEventModal;
	};

	// Function to adjust the height of the textarea dynamically
	function adjustTextareaHeight(event) {
		const textarea = event.target;
		textarea.style.height = 'auto'; // Reset the height
		textarea.style.height = `${textarea.scrollHeight}px`; // Set the height to the scroll height
	}

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
					Authorization: `Bearer ${access_token}`
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

	// Fetch user communities
	async function fetchManagedEvents() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/events/managed/', {
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch communities: ${response.status}`);
			}

			const data = await response.json();
			console.log('API Response for user communities:', data); // Log the full response

			// Check if the response is an array
			if (Array.isArray(data)) {
				managedEvents = data; // Directly assign the array to 'communities'
				allowedToEdit = managedEvents.length > 0;
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

		console.log('Form submission triggered.');

		const eventData = {
			title,
			description,
			date,
			virtual_link: virtualLinkInput.trim() || null,
			location: locationInput.trim() || null,
			event_type,
			community_id
		};

		// Log event data, including community_id
		console.log('Event Data:', eventData);

		try {
			console.log('Sending POST request to API...');

			const response = await fetch('http://127.0.0.1:8000/api/events/create/', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/x-www-form-urlencoded'
				},
				body: new URLSearchParams(eventData) // Using URLSearchParams to encode the form data
			});

			// Check for a successful response
			if (!response.ok) {
				const errorText = await response.text();
				console.error('Error:', errorText); // Log error response body
				alert(`Error: ${errorText}`);
				return;
			}

			// Parse the JSON response
			const result = await response.json();
			console.log('Event created successfully:', result); // Log success
			window.location.reload();
		} catch (error) {
			console.error('Error creating event:', error); // Log error in case of failure
		}
	}

	// Submit event form
	async function submitEditEvent(event) {
		event.preventDefault(); // Prevent default form submission

		let value = null;
		switch (selectedEventEditCategory) {
			case 'title':
				value = editTitle;
				break;
			case 'description':
				value = editDescription;
				break;
			case 'date':
				value = editDate;
				break;
			case 'virtual_link':
				value = editVirtualLink;
				break;
			case 'location':
				value = editLocation;
				break;
			case 'event_type':
				value = editEventType;
				break;
		}

		const editData = {
			field: selectedEventEditCategory,
			value,
			eventId: editEventId
		};

		try {
			console.log('Sending POST request to API...');

			const response = await fetch('http://127.0.0.1:8000/api/events/manage/', {
				method: 'PATCH',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(editData)
			});

			// Check for a successful response
			if (!response.ok) {
				const errorText = await response.text();
				console.error('Error:', errorText); // Log error response body
				alert(`Error: ${errorText}`);
				return;
			}

			window.location.reload();
		} catch (error) {
			console.error('Error creating event:', error); // Log error in case of failure
		}
	}

	// Fetch events
	async function fetchEvents() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/events/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`
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

	// Function to handle action change for community management commands
	function handleSelectedEventEditCategory(event) {
		selectedEventEditCategory = event.target.value;
	}

	// Join event function
	async function joinEvent(eventId) {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/events/${eventId}/join/`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.error || 'Failed to join event');
			}

			const result = await response.json();
			console.log('Successfully joined event:', result);

			// Refresh the events list to update the UI
			await fetchEvents();
		} catch (error) {
			console.error('Error joining event:', error);
			alert(error.message);
		}
	}

	// Leave event function
	async function leaveEvent(eventId) {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/events/${eventId}/leave/`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/json'
				}
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.error || 'Failed to leave event');
			}

			console.log('Successfully left event:', data);

			// Refresh the events list to update the UI
			await fetchEvents();
		} catch (error) {
			console.error('Error leaving event:', error);
			alert(error.message);
		}
	}

	async function cancelEvent(eventId) {
		try {
			const response = await fetch(`http://127.0.0.1:8000/api/events/${eventId}/cancel/`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				alert('Event cancelled!');
				// You could reload or redirect here
			} else {
				const error = await response.json();
				alert('Failed to cancel event: ' + error.detail);
			}
		} catch (error) {
			console.error('Error cancelling event:', error);
		}
	}

	$: filteredEvents = events.filter((e) => {
		const lowerSearch = searchTerm.toLowerCase();
		return (
			e.title.toLowerCase().includes(lowerSearch) ||
			e.description.toLowerCase().includes(lowerSearch) ||
			e.event_type.toLowerCase().includes(lowerSearch) ||
			(e.location && e.location.toLowerCase().includes(lowerSearch)) ||
			(e.date && e.date.toLowerCase().includes(lowerSearch)) ||
			(e.community && e.community.toLowerCase().includes(lowerSearch)) ||
			(e.virtual_link && e.virtual_link.toLowerCase().includes(lowerSearch))
		);
	});

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
			await fetchManagedEvents();
			const response = await fetch('http://127.0.0.1:8000/api/communities/', {
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			const allCommunities = await response.json();

			const permitted = [];
			console.log('Communities:', communities);

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
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
		<!-- Create Event Form -->
		{#if allowedToCreate && showEventModal}
			<div
				style="background-color: rgba(0, 0, 0, 0.8);"
				class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
				on:click={toggleEventModal}
			>
				<div class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-3xl" on:click|stopPropagation>
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">Create Event</h1>
					<form on:submit|preventDefault={submitEvent} id="createEventForm" class="form-container">
						<!-- Community Selection -->
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="community" class="label">
									<span class="label-text">Community</span>
								</label>
								<div class="relative">
									<select
										id="community"
										bind:value={community_id}
										required
										class="select select-bordered validator custom-input placeholder-selected"
									>
										<option value="" disabled selected>Select a community</option>
										{#if communities.length === 0}
											<option disabled>No communities found</option>
										{:else}
											{#each communities as community}
												<option value={community.community_id}>{community.name}</option>
											{/each}
										{/if}
									</select>
								</div>
							</div>
						</div>
						<!-- Title Input -->
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row w-full">
							<div class="w-full">
								<label for="title" class="label">
									<span class="label-text">Title</span>
								</label>
								<div class="relative">
									<input
										type="text"
										id="title"
										bind:value={title}
										required
										class="input input-bordered validator custom-input"
										placeholder="What's your event's title?"
									/>
								</div>
							</div>
						</div>
						<!-- Description Input -->
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
										placeholder="What's your event's description?"
										on:input={adjustTextareaHeight}
									/>
								</div>
							</div>
						</div>
						<!-- Date Input -->
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="date" class="label">
									<span class="label-text">Date</span>
								</label>
								<div class="relative">
									<input
										type="date"
										id="date"
										bind:value={date}
										required
										class="input input-bordered validator custom-input placeholder-selected"
										placeholder="When is the event?"
									/>
								</div>
							</div>
						</div>
						<!-- Type Input -->
						<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="event_type" class="label">
									<span class="label-text">Type</span>
								</label>
								<div class="relative">
									<select
										id="event_type"
										bind:value={event_type}
										required
										class="select select-bordered validator custom-input placeholder-selected"
									>
										<option value="" disabled selected>Is it virtual or in person event?</option>
										<option value="in-person">In-Person</option>
										<option value="virtual">Virtual</option>
									</select>
								</div>
							</div>
						</div>
						<!-- Location Input -->
						{#if event_type === 'in-person'}
							<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row w-full">
								<div class="w-full">
									<label for="location" class="label">
										<span class="label-text">Venue</span>
									</label>
									<div class="relative">
										<input
											type="text"
											id="location"
											bind:value={locationInput}
											required
											class="input input-bordered validator custom-input"
											placeholder="Where's the location of the event?"
										/>
									</div>
								</div>
							</div>
						{/if}

						<!-- Virtual Link Input -->
						{#if event_type === 'virtual'}
							<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row w-full">
								<div class="w-full">
									<label for="virtual_link" class="label">
										<span class="label-text">Virtual Link</span>
									</label>
									<div class="relative">
										<input
											type="url"
											id="location"
											bind:value={virtualLinkInput}
											required
											class="input input-bordered validator custom-input placeholder-selected"
											placeholder="Type the link to your event"
										/>
									</div>
								</div>
							</div>
						{/if}

						<!-- Submit Button -->
						<div class="mb-2 mt-2 flex justify-center text-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								type="submit">Create</button
							>
						</div>
					</form>
				</div>
			</div>
		{/if}

		<div class="card bg-base-100 w-full rounded-3xl">
			<div class="card-body bg-secondary rounded-3xl">
				{#if allowedToEdit}
					<!-- Your form fields here -->
					<form on:submit={submitEditEvent} id="createEventForm" class="form-container">
						<div class="relative flex items-center">
							<select
								type="text"
								bind:value={editEventId}
								required
								class="select select-bordered custom-input flex-grow"
							>
								<option value={null} selected>Select an Event</option>
								{#each managedEvents as event}
									<option value={event.event_id}>{event.title}</option>
								{/each}
							</select>
						</div>
						{#if editEventId}
							<div class="w-full">
								<label for="action" class="label">
									<span class="label-text">What would you like to do?</span>
								</label>
								<div class="relative flex items-center">
									<select
										id="action"
										bind:value={selectedEventEditCategory}
										required
										class="select select-bordered custom-input flex-grow"
										on:change={handleSelectedEventEditCategory}
									>
										<option value="" disabled selected>Select an Action</option>
										<option value="title">Change Event Title</option>
										<option value="description">Change Event Description</option>
										<option value="date">Change Event Date</option>
										<option value="virtual_link">Change Event Link</option>
										<option value="location">Change Event Location</option>
										<option value="event_type">Change Event Type</option>
									</select>
								</div>
							</div>
						{/if}
						{#if selectedEventEditCategory == 'title'}
							<div class="form-group">
								<label for="title">Title:</label>
								<input
									type="text"
									bind:value={editTitle}
									id="title"
									class="input bg-white"
									required
								/>
							</div>
						{/if}
						{#if selectedEventEditCategory == 'description'}
							<div class="form-group">
								<label for="description">Description:</label>
								<textarea
									bind:value={editDescription}
									id="description"
									class="input bg-white"
									required
								></textarea>
							</div>
						{/if}
						{#if selectedEventEditCategory == 'date'}
							<div class="form-group">
								<label for="date">Date:</label>
								<input
									type="date"
									bind:value={editDate}
									id="date"
									class="input bg-white"
									required
								/>
							</div>
						{/if}
						{#if selectedEventEditCategory == 'virtual_link'}
							<div class="form-group">
								<label for="virtual_link">Virtual Link:</label>
								<input
									type="url"
									bind:value={editVirtualLink}
									id="virtual_link"
									class="input bg-white"
								/>
							</div>
						{/if}
						{#if selectedEventEditCategory == 'location'}
							<div class="form-group">
								<label for="location">Location:</label>
								<input type="text" bind:value={editLocation} id="location" class="input bg-white" />
							</div>
						{/if}
						{#if selectedEventEditCategory == 'event_type'}
							<div class="form-group">
								<label for="event_type">Event Type:</label>
								<select bind:value={editEventType} id="event_type" class="select bg-white" required>
									<option value="virtual">Virtual</option>
									<option value="in-person">In-Person</option>
								</select>
							</div>
						{/if}
						<button type="submit" class="submit-btn">Update Event</button>
					</form>
				{:else}
					<p>No managed events to edit</p>
				{/if}
			</div>
		</div>
	</div>
	{#each filteredEvents as event}
		<!-- Events List -->
		<div class="card bg-base-100 w-full rounded-3xl mt-5">
			<div class="card-body bg-secondary rounded-3xl">
				<h2>Your Events</h2>
				{#if events.length === 0}
					<p>No events available.</p>
				{:else}
					<div class="events-list">
						<div class="event-card">
							<h3>{event.title}</h3>
							<p>{event.description}</p>
							<p><strong>Date:</strong> {event.date}</p>
							<p><strong>Event Type:</strong> {event.event_type}</p>
							<p><strong>Location:</strong> {event.location || 'Online'}</p>
							{#if event.virtual_link}
								<p>
									<strong>Virtual Link:</strong>
									<a href={event.virtual_link} target="_blank">Join Event</a>
								</p>
							{/if}
							<p><strong>Community:</strong> {event.community}</p>
							{#if !event.is_owner}
								{#if !event.is_participating}
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto mt-3"
									on:click={() => joinEvent(event.event_id)}
								>
									Join Event
								</button>
								{:else}
								<div class="flex flex-col items-start gap-2">
									<p class="text-primary mt-3">You are participating in this event</p>
									<button
									class="btn btn-error text-secondary hover:bg-error-focus w-fit"
									on:click={() => leaveEvent(event.event_id)}
									>
									Leave Event
									</button>
								</div>
								{/if}
							{/if}

						<!-- Show Cancel Event button only if the user is the owner or a leader -->
						{#if event.can_cancel}
							<button
							class="btn bg-primary text-white hover:bg-primary-focus w-full mt-2"
							on:click={() => cancelEvent(event.event_id)}
							>
							Cancel Event
							</button>
						{/if}
						</div>
					</div>
				{/if}
			</div>
		</div>
	{/each}

	<!-- Floating Add Button -->
	<button
		class="fixed bottom-5 right-5 bg-primary text-secondary p-4 rounded-full shadow-lg hover:bg-primary-focus z-50"
		on:click={toggleEventModal}
	>
		<AddIconNoCircle size={28} />
	</button>
</main>
