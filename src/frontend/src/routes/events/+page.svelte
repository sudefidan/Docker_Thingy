<script>
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";

    let title = "";
    let description = "";
    let date = "";
    let virtual_link = "";
    let location = "";
    let event_type = "";
    let community = "";

    let eventTypes = [];
    let communities = [];
    let users = [];
    let allowedCommunities = [];

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

    const fetchEventData = async () => {
        try {
            const response = await Promise.all([
			fetch("http://127.0.0.1:8000/api/event-types/", {
				method: "GET",
				headers: { Authorization: `Bearer ${access_token}` },
			}),
			fetch("http://127.0.0.1:8000/api/communities/", {
				method: "GET",
				headers: { Authorization: `Bearer ${access_token}` },
			}),
		]);

        const eventTypesRes = await response [0].json();
        const communityRes  = await response [1].json();

        eventTypes = eventTypesRes;
        communities = communityRes;

        allowedCommunities = communities.filter(({id}) =>
        users.owned_communities.concat(users.leader_communities).includes.id

        );
        }   catch (error) {
			    console.error('Network error:', error.message);
        }
    };

    async function submitForm() {
        if (!community || !allowedCommunities.some(({ id }) => id === community)) {
            return("You are not allowed to create events in this community!");
    }

    try{
        const response = await fetch("http://127.0.0.1:8000/api/events/",{
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, description, date, virtual_link, location, event_type, community })
      });

      if (response.ok) {
        alert("Event Created Successfully!"); // Notify the user
        goto("/events");  // Redirect to the events page
    } else {
        console.error("Failed to create event.");
        }
        } catch (error) {
        console.error("Error creating event:", error);
        }
    }
</script>

<!-- UI -->

<div class="space-y-10">
    <div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
      <div class="card-body bg-secondary rounded-3xl">
        <h1 class="text-primary text-4xl font-bold text-center">Create a New Event</h1>
  
        {#if users}
          {#if allowedCommunities.length > 0}
            <!-- Event Creation Form -->
            <form id="event-form" on:submit|preventDefault={submitForm} class="flex flex-col space-y-4 p-6">
              
              <!-- Title Input -->
                <label for="title" class="text-lg font-semibold text-primary">Title:</label>
                <input id="title" type="text" bind:value={title} required class="input input-bordered w-full" />

                <!-- Description Input -->
                <label for="description" class="text-lg font-semibold text-primary">Description:</label>
                <textarea id="description" bind:value={description} required class="textarea textarea-bordered w-full"></textarea>

                <!-- Date Picker -->
                <label for="date" class="text-lg font-semibold text-primary">Date:</label>
                <input id="date" type="date" bind:value={date} required class="input input-bordered w-full" />

                <!-- Virtual Link (Optional) -->
                <label for="virtual_link" class="text-lg font-semibold text-primary">Virtual Link:</label>
                <input id="virtual_link" type="url" bind:value={virtual_link} class="input input-bordered w-full" placeholder="https://enteryourlink.com" />

                <!-- Location Input -->
                <label for="location" class="text-lg font-semibold text-primary">Location:</label>
                <input id="location" type="text" bind:value={location} required class="input input-bordered w-full" />

                <!-- Event Type Dropdown -->
                <label for="event_type" class="text-lg font-semibold text-primary">Event Type:</label>
                <select id="event_type" bind:value={event_type} required class="select select-bordered w-full">
                <option value="">Select Event Type</option>
                {#each eventTypes as type}
                    <option value={type.id}>{type.name}</option>
                {/each}
                </select>

                <!-- Community Dropdown (Only allowed communities) -->
                <label for="community" class="text-lg font-semibold text-primary">Community:</label>
                <select id="community" bind:value={community} required class="select select-bordered w-full">
                <option value="">Select Community</option>
                {#each allowedCommunities as comm}
                    <option value={comm.id}>{comm.name}</option>
                {/each}
                </select>
  
              <!-- Submit Button -->
              <button type="submit" class="bg-blue-500 text-white px-6 py-3 rounded-lg text-lg font-semibold hover:bg-blue-600 transition">
                Create Event
              </button>
            </form>
          {:else}
            <!-- If the user is not authorized to create events -->
            <p class="text-center text-lg text-red-500">You are not authorized to create events.</p>
          {/if}
        {:else}
          <!-- Loading message while fetching data -->
          <p class="text-center text-lg text-gray-500">Loading...</p>
        {/if}
      </div>
    </div>
  </div>