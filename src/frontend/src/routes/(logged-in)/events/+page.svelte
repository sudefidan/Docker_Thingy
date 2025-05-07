<script>
	import { onMount } from 'svelte';
	import AddIconNoCircle from '../../../assets/AddIconNoCircle.svelte';
	import AddIcon from '../../../assets/AddIcon.svelte';
	import SettingsIcon from '../../../assets/SettingsIcon.svelte';

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
	let showEventManagementModal = false;
	let selectedEventId = null;
	let subscribedCommunityIds = []; // Stores IDs of communities the user is subscribed to
	let selectedEventAction = '';
	let maxCapacityInput = 20;
	let materials = '';

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
	let editCapacity = '';
	let editMaterials = '';

	// Function to toggle event management modal
	const toggleEventManagementModal = (eventId) => {
		selectedEventId = eventId;
		if (eventId) {
			// Prefill form fields with the selected event's data
			const selectedEvent = events.find((e) => e.event_id === eventId);
			if (selectedEvent) {
				editTitle = selectedEvent.title;
				editDescription = selectedEvent.description;
				editDate = selectedEvent.date;
				editEventType = selectedEvent.event_type;
				editMaterials = selectedEvent.materials || '';

				// Initialise location and virtual link fields based on event type
				if (selectedEvent.event_type === 'virtual') {
					editVirtualLink = selectedEvent.virtual_link || '';
					editLocation = ''; // Clear location field for virtual events
				} else {
					editLocation = selectedEvent.location || '';
					editVirtualLink = ''; // Clear virtual link field for in-person events
				}
			}
		} else {
			// Reset form fields when closing the modal
			editTitle = '';
			editDescription = '';
			editDate = '';
			editVirtualLink = '';
			editLocation = '';
			editEventType = '';
			editMaterials = '';
		}
		showEventManagementModal = !showEventManagementModal;
		selectedEventAction = '';
	};

	// Function to handle event action change
	function handleEventActionChange(event) {
		selectedEventAction = event.target.value;
	}

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

	// Fetch IDs of communities the user is subscribed to
	async function fetchSubscribedCommunityIds() {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/subscribed_communities/', {
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (!response.ok) {
				throw new Error(`Failed to fetch subscribed communities: ${response.status}`);
			}
			const data = await response.json();
			if (data && Array.isArray(data.subscribed_communities)) {
				subscribedCommunityIds = data.subscribed_communities.map((comm) => comm.id);
				console.log('Fetched subscribed community IDs:', subscribedCommunityIds);
			} else {
				console.error('Subscribed communities data is not in the expected format:', data);
				subscribedCommunityIds = [];
			}
		} catch (error) {
			console.error('Error fetching subscribed community IDs:', error);
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
			community_id,
			max_capacity: maxCapacityInput,
			materials
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

	// Function to update event
	async function updateEvent(field, value, skipReload = false) {
		try {
			const editData = {
				field,
				value,
				eventId: selectedEventId
			};

			const response = await fetch('http://127.0.0.1:8000/api/events/manage/', {
				method: 'PATCH',
				headers: {
					Authorization: `Bearer ${access_token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(editData)
			});

			if (!response.ok) {
				const errorText = await response.text();
				console.error('Error:', errorText);
				alert(`Error: ${errorText}`);
				return;
			}

			// Only reload if skipReload is false
			if (!skipReload) {
				// Success - reload page
				alert('Event updated successfully');
				window.location.reload();
			}

			return true; // Indicate success
		} catch (error) {
			console.error('Error updating event:', error);
		}
	}

	// Function to handle event type changes
	async function handleEventTypeChange() {
		try {
			// First update the event type (skip reload)
			const typeUpdated = await updateEvent('event_type', editEventType, true);
			if (!typeUpdated) return;

			let locationUpdated = true;

			// Next, update either location or virtual link based on the new event type
			if (editEventType === 'virtual' && editVirtualLink) {
				locationUpdated = await updateEvent('virtual_link', editVirtualLink, true);
				if (locationUpdated) {
					// Clear the location since it's a virtual event
					await updateEvent('location', null, true);
				}
			} else if (editEventType === 'in-person' && editLocation) {
				locationUpdated = await updateEvent('location', editLocation, true);
				if (locationUpdated) {
					// Clear the virtual link since it's an in-person event
					await updateEvent('virtual_link', null, true);
				}
			}

			if (!locationUpdated) return;

			// Show success message
			alert('Event updated successfully!');
			toggleEventManagementModal(null); // Close the modal

			// Reload the page
			window.location.reload();
		} catch (error) {
			console.error('Error updating event type:', error);
			alert('Failed to update event. Please try again.');
		}
	}

	// Updated cancelEvent function
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
				alert('Event cancelled successfully!');
				window.location.reload();
			} else {
				const error = await response.json();
				alert('Failed to cancel event: ' + error.detail);
			}
		} catch (error) {
			console.error('Error cancelling event:', error);
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

	$: filteredEvents = events
		.filter((e) => {
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
		})
		.sort((eventA, eventB) => {
			const getPriority = (event) => {
				let calculatedPriority;

				if (event.is_participating) {
					// User has joined the event
					if (event.is_owner) {
						calculatedPriority = 1; // Priority 1: Owned by user, and user has joined
					} else if (event.can_cancel) {
						calculatedPriority = 3; // Priority 3: Led by user (not owned), and user has joined
					} else {
						calculatedPriority = 5; // Priority 5: Regular Joined (not in a community owned or led by user)
					}
				} else {
					// User has NOT joined the event
					if (event.is_owner) {
						calculatedPriority = 2; // Priority 2: Owned by user, but user has NOT joined
					} else if (event.can_cancel) {
						calculatedPriority = 4; // Priority 4: Led by user (not owned), and user has NOT joined
					} else if (subscribedCommunityIds.includes(Number(event.community_id))) {
						// Convert event.community_id to Number
						calculatedPriority = 6; // Priority 6: Unjoined, in a subscribed community (not owned/led by user)
					} else {
						calculatedPriority = 7; // Priority 7: Other unjoined events
					}
				}

				return calculatedPriority;
			};

			const priorityA = getPriority(eventA);
			const priorityB = getPriority(eventB);

			if (priorityA < priorityB) return -1;
			if (priorityA > priorityB) return 1;

			// Optional: Add secondary sorting criteria here if priorities are the same, e.g., by date
			// For now, maintain original relative order for events with the same priority.
			return 0;
		});

	// Run the functions when the component loads
	onMount(async () => {
		try {
			// Get the access token from local storage
			access_token = localStorage.getItem('access_token');

			// Redirect to login page if no token found
			if (!access_token) {
				goto('http://localhost:5173/');
				return;
			}

			// Extract user ID from the JWT token
			loggedInUserId = getLoggedInUserIdFromToken(access_token);

			await fetchUsers(); // Load all users for the user selection UI
			await fetchUserCommunities(); // Load communities the user is part of
			await fetchEvents(); // Load all events to display
			await fetchManagedEvents(); // Load events the user can manage
			await fetchSubscribedCommunityIds(); // Load IDs of subscribed communities for sorting

			// Fetch all communities from the server
			const response = await fetch('http://127.0.0.1:8000/api/communities/', {
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});
			if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
			const allCommunities = await response.json();

			// This array will store communities the user is allowed to create events for
			const permitted = [];
			console.log('Communities:', communities);

			// Check each community to see if user is owner or leader
			for (const community of allCommunities) {
				// Check if user is the owner of this community
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

				// Check if user is a leader of this community
				const isLeader = leaders.some((leader) => leader.user_id === loggedInUserId);

				// If user is either owner or leader, add community to permitted list
				if (isOwner || isLeader) {
					permitted.push(community);
				}
			}

			// Update the communities array with only those the user can create events for
			communities = permitted;

			// Set the flag that determines if the "Create Event" button should be shown
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
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4 w-full">
		<!-- Create Event Form -->
		{#if allowedToCreate && showEventModal}
			<div
				style="background-color: rgba(0, 0, 0, 0.8);"
				class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
				on:click={toggleEventModal}
			>
				<div
					class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-3xl"
					on:click|stopPropagation
				>
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
						<!-- Required materials Input -->
						<div class="form-control mb-5">
							<label class="label"><span class="label-text">Required Materials</span></label>
							<input
								type="text"
								bind:value={materials}
								class="input input-bordered"
								placeholder="E.g. Zoom link, handout PDF, lab coat…"
							/>
						</div>

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
						<!-- Max Capacity Input -->
						<div class="form-control mb-5">
							<label class="label"><span class="label-text">Capacity</span></label>
							<input
								type="number"
								bind:value={maxCapacityInput}
								min="1"
								class="input input-bordered"
								placeholder="Max attendees"
								required
							/>
						</div>

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

		<!-- Event Management Modal -->
		{#if showEventManagementModal}
			<div
				style="background-color: rgba(0, 0, 0, 0.8);"
				class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
				on:click={() => toggleEventManagementModal(null)}
			>
				<div
					class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-3xl"
					on:click|stopPropagation
				>
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">
						Manage Event: {events.find((e) => e.event_id === selectedEventId)?.title}
					</h1>
					<div class="form-control mb-2 flex flex-col gap-3">
						<label for="action" class="label">
							<span class="label-text">What would you like to do?</span>
						</label>
						<div class="relative flex items-center">
							<select
								id="action"
								bind:value={selectedEventAction}
								required
								class="select select-bordered custom-input flex-grow placeholder-selected"
								on:change={handleEventActionChange}
							>
								<option value="" disabled selected>Select an Action</option>
								<option value="changeTitle">Change Event Title</option>
								<option value="changeDescription">Change Event Description</option>
								<option value="changeDate">Change Event Date</option>
								<option value="changeEventType">Change Event Type</option>
								<option value="changeCapacity">Change Capacity</option>
								<option value="changeMaterials">Change Materials</option>

								<!-- Show virtual link option only for virtual events -->
								{#if events.find((e) => e.event_id === selectedEventId)?.event_type === 'virtual'}
									<option value="changeVirtualLink">Change Virtual Link</option>
								{/if}

								<!-- Show location option only for in-person events -->
								{#if events.find((e) => e.event_id === selectedEventId)?.event_type === 'in-person'}
									<option value="changeLocation">Change Location</option>
								{/if}

								<option value="cancelEvent">Cancel Event</option>
							</select>
						</div>
					</div>

					{#if selectedEventAction === 'changeCapacity'}
						<div class="form-control mb-4 flex flex-col gap-3">
							<label for="capacity" class="label">
								<span class="label-text">New Capacity</span>
							</label>
							<input
								id="capacity"
								type="number"
								bind:value={editCapacity}
								min="1"
								class="input input-bordered"
								placeholder="Enter new max attendees"
								required
							/>
							<button
								class="btn btn-primary mt-2"
								on:click={() => {
									updateEvent('max_capacity', editCapacity);
									selectedEventAction = '';
								}}
							>
								Update Capacity
							</button>
						</div>
					{/if}

					<!-- Change Title -->
					{#if selectedEventAction === 'changeTitle'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="title" class="label">
									<span class="label-text">New Title</span>
								</label>
								<div class="relative flex items-center">
									<input
										type="text"
										bind:value={editTitle}
										required
										class="input input-bordered validator custom-input"
										placeholder="Enter new title..."
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => updateEvent('title', editTitle)}>Update</button
								>
							</div>
						</div>
					{/if}

					<!-- Change Description -->
					{#if selectedEventAction === 'changeDescription'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="description" class="label">
									<span class="label-text">New Description</span>
								</label>
								<div class="relative flex items-center">
									<textarea
										bind:value={editDescription}
										required
										class="input input-bordered text-area-input"
										placeholder="Enter new description..."
										on:input={adjustTextareaHeight}
									></textarea>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => updateEvent('description', editDescription)}>Update</button
								>
							</div>
						</div>
					{/if}

					<!-- Change Date -->
					{#if selectedEventAction === 'changeDate'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="date" class="label">
									<span class="label-text">New Date</span>
								</label>
								<div class="relative flex items-center">
									<input
										type="date"
										bind:value={editDate}
										required
										class="input input-bordered validator custom-input"
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => updateEvent('date', editDate)}>Update</button
								>
							</div>
						</div>
					{/if}

					<!-- Change Virtual Link -->
					{#if selectedEventAction === 'changeVirtualLink'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="virtual_link" class="label">
									<span class="label-text">New Virtual Link</span>
								</label>
								<div class="relative flex items-center">
									<input
										type="url"
										bind:value={editVirtualLink}
										required
										class="input input-bordered validator custom-input"
										placeholder="Enter new virtual link..."
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => updateEvent('virtual_link', editVirtualLink)}>Update</button
								>
							</div>
						</div>
					{/if}

					<!-- Change Location -->
					{#if selectedEventAction === 'changeLocation'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="location" class="label">
									<span class="label-text">New Location</span>
								</label>
								<div class="relative flex items-center">
									<input
										type="text"
										bind:value={editLocation}
										required
										class="input input-bordered validator custom-input"
										placeholder="Enter new location..."
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => updateEvent('location', editLocation)}>Update</button
								>
							</div>
						</div>
					{/if}

					{#if selectedEventAction === 'changeMaterials'}
						<div class="form-control mb-4 flex flex-col gap-3">
							<label for="materials" class="label">
								<span class="label-text">New Materials</span>
							</label>
							<input
								id="materials"
								type="text"
								bind:value={editMaterials}
								class="input input-bordered"
								placeholder="e.g. Slides, PDF, Zoom link…"
							/>
							<button
								class="btn btn-primary mt-2"
								on:click={() => {
									updateEvent('materials', editMaterials);
									selectedEventAction = '';
								}}>Update Materials</button
							>
						</div>
					{/if}

					<!-- Change Event Type -->
					{#if selectedEventAction === 'changeEventType'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="event_type" class="label">
									<span class="label-text">New Event Type</span>
								</label>
								<div class="relative flex items-center">
									<select
										id="event_type"
										bind:value={editEventType}
										required
										class="select select-bordered custom-input placeholder-selected"
										on:change={() => {
											// Clear the fields when switching event types
											if (editEventType === 'virtual') {
												editLocation = ''; // Clear location when switching to virtual
											} else {
												editVirtualLink = ''; // Clear virtual link when switching to in-person
											}
										}}
									>
										<option value="virtual">Virtual</option>
										<option value="in-person">In-Person</option>
									</select>
								</div>
							</div>
							<!-- Show virtual link input immediately if "virtual" is selected -->
							{#if editEventType === 'virtual' && events.find((e) => e.event_id === selectedEventId)?.event_type !== 'virtual'}
								<div class="w-full mt-3">
									<label for="virtual_link" class="label">
										<span class="label-text">Virtual Link</span>
									</label>
									<div class="relative flex items-center">
										<input
											type="url"
											id="virtual_link"
											bind:value={editVirtualLink}
											required
											class="input input-bordered validator custom-input"
											placeholder="Enter virtual meeting link..."
										/>
									</div>
								</div>
							{/if}
							<!-- Show location input immediately if "in-person" is selected -->
							{#if editEventType === 'in-person' && events.find((e) => e.event_id === selectedEventId)?.event_type !== 'in-person'}
								<div class="w-full mt-3">
									<label for="location" class="label">
										<span class="label-text">Location</span>
									</label>
									<div class="relative flex items-center">
										<input
											type="text"
											id="location"
											bind:value={editLocation}
											required
											class="input input-bordered validator custom-input"
											placeholder="Enter location..."
										/>
									</div>
								</div>
							{/if}

							<div class="mb-2 mt-4 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={handleEventTypeChange}>Update</button
								>
							</div>
						</div>
					{/if}

					<!-- Cancel Event -->
					{#if selectedEventAction === 'cancelEvent'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="mb-2 mt-2 flex justify-center">
								<button
									class="btn btn-error text-secondary hover:bg-error-focus w-auto pl-10 pr-10"
									on:click={() => cancelEvent(selectedEventId)}>Cancel Event</button
								>
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}
		{#each filteredEvents as event}
			<div class="card bg-base-100 w-full rounded-3xl mt-5">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow">
							<h3 class="text-primary text-2xl font-bold">{event.title}</h3>
						</div>

						<!-- Show "Manage" button if user is the organizer/owner of the event -->
						{#if event.is_owner}
							<div class="tooltip-container">
								<button
									on:click={() => toggleEventManagementModal(event.event_id)}
									class="hover:text-primary"
									aria-label="Manage Event"
								>
									<SettingsIcon />
								</button>
								<span class="tooltip">Manage this event</span>
							</div>
						{/if}

						<!-- Show "Leave" button if user is participating and not the owner -->
						{#if event.is_participating && !event.is_owner}
							<div class="tooltip-container">
								<button
									on:click={() => leaveEvent(event.event_id)}
									class="hover:text-primary"
									aria-label="Leave Event"
								>
									<svg
										xmlns="http://www.w3.org/2000/svg"
										fill="currentColor"
										class="bi bi-box-arrow-right size-7"
										viewBox="0 0 16 16"
									>
										<path
											fill-rule="evenodd"
											d="M10 12.5a.5.5 0 0 1-.5.5h-8a.5.5 0 0 1-.5-.5v-9a.5.5 0 0 1 .5-.5h8a.5.5 0 0 1 .5.5v2a.5.5 0 0 0 1 0v-2A1.5 1.5 0 0 0 9.5 2h-8A1.5 1.5 0 0 0 0 3.5v9A1.5 1.5 0 0 0 1.5 14h8a1.5 1.5 0 0 0 1.5-1.5v-2a.5.5 0 0 0-1 0z"
										/>
										<path
											fill-rule="evenodd"
											d="M15.854 8.354a.5.5 0 0 0 0-.708l-3-3a.5.5 0 0 0-.708.708L14.293 7.5H5.5a.5.5 0 0 0 0 1h8.793l-2.147 2.146a.5.5 0 0 0 .708.708z"
										/>
									</svg>
								</button>
								<span class="tooltip">Leave this event</span>
							</div>
							<!-- Show "Join" button if the user is not participating -->
						{:else if !event.is_participating && !event.is_owner && !event.is_full}
							<div class="tooltip-container">
								<button on:click={() => joinEvent(event.event_id)} class="hover:text-primary">
									<AddIcon />
								</button>
								<span class="tooltip">Join this event</span>
							</div>
						{/if}
					</div>

					<div class="mt-2">
						<button
							class="btn btn-outline w-full"
							on:click={() =>
								alert(
									`${event.participant_count} joined, ${event.max_capacity - event.participant_count} spots left`
								)}
						>
							{event.participant_count}/{event.max_capacity} spots used
						</button>
					</div>

					<div class="event-details">
						<p>{event.description}</p>
						<p><strong>Date:</strong> {event.date}</p>
						<p><strong>Community:</strong> {event.community}</p>
						{#if event.event_type === 'in-person' && event.location}
							<p>
								<strong>Location:</strong>
								{event.location}
							</p>
						{:else if event.event_type === 'virtual' && event.virtual_link}
							<p>
								<strong>Link:</strong>
								<a href={event.virtual_link} target="_blank">{event.virtual_link}</a>
							</p>
						{:else}
							<p><strong>Location:</strong> Online</p>
						{/if}

						{#if event.materials}
							<p><strong>Materials:</strong> {event.materials}</p>
						{/if}
					</div>
				</div>
			</div>
		{/each}

		<!-- Floating Add Button -->
		{#if allowedToCreate}
			<button
				class="fixed bottom-5 right-5 bg-primary text-secondary p-4 rounded-full shadow-lg hover:bg-primary-focus z-50"
				on:click={toggleEventModal}
			>
				<AddIconNoCircle size={28} />
			</button>
		{/if}
	</div>
</main>
