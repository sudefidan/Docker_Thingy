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
			console.log("User's List", usersList);
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
				console.log('User ID:', loggedInUserId);
				console.log('Subscribed Communities:', subscribedCommunities);
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
				console.log('All Users:', users);
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
			console.log('communities:', communities);
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
				alert('Community created successfully!');
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
				await fetchSubscribedCommunities();
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
				console.log('Current Community Leaders:', community_leaders);
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
			<!-- Communities Section-->
			<div class="flex flex-wrap justify-center space-y-2">
				<!-- List Communities and Join Button -->

				{#each communities as community}
					<div class="card bg-base-100 w-full rounded-3xl">
						<div class="card-body bg-secondary rounded-3xl">
							<div class="mb-4 flex items-center justify-between">
								<div class="flex-grow text-center">
									<h1 class="text-primary text-4xl font-bold">{community.name}</h1>
								</div>
								<!-- Show "Leave" button if the user is subscribed and not the owner of the community -->
								{#if subscribedCommunities.some((sub) => sub.id === community.community_id) && community.owner_id != loggedInUserId}
									<div class="tooltip-container">
										<button
											on:click={() => leave_community(community.community_id)}
											class="hover:text-primary"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="currentColor"
												class="bi bi-box-arrow-right size-6"
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
										<span class="tooltip">Leave this community</span>
									</div>
									<!-- Show "Join" button if the user is not subscribed, or leader or owner -->
								{:else if !subscribedCommunities.some((sub) => sub.id === community.community_id)}
									<div class="tooltip-container">
										<button
											on:click={() => join_community(community.community_id)}
											class="hover:text-primary"
											title="Join this community"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												width="16"
												height="16"
												fill="currentColor"
												class="bi bi-plus-circle size-6"
												viewBox="0 0 16 16"
											>
												<path
													d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14m0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16"
												/>
												<path
													d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4"
												/>
											</svg>
										</button>
										<span class="tooltip">Join this community</span>
									</div>
								{/if}
							</div>
							<div class="mb-4">
								<p>Category: {community.category}</p>
								<p class="community-description">{community.description}</p>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
		<!-- Right Column -->
		<div class="space-y-10">
			<!-- Community Management -->
			<div class="card bg-base-100 shadow-4xl w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">Community Management</h1>
					<div class="form-control mb-2 flex flex-col gap-3">
						<div class="w-full">
							<label for="name" class="label">
								<span class="label-text">Which one of your communities do you want to change?</span>
							</label>
							<div class="relative flex items-center">
								<select
									type="text"
									bind:value={community_management_selected}
									required
									class="select select-bordered custom-input flex-grow"
									on:change={get_community_leaders}
								>
									<option value={null}>Select a Community</option>
									{#each communities as community}
										{#if community.owner_id === loggedInUserId}
											<option value={community.community_id}>{community.name}</option>
										{/if}
									{/each}
								</select>
							</div>
						</div>
						{#if community_management_selected}
							<div class="w-full">
							<label for="action" class="label">
								<span class="label-text">What would you like to do?</span>
							</label>
							<div class="relative flex items-center">
								<select
									id="action"
									bind:value={selectedAction}
									required
									class="select select-bordered custom-input flex-grow"
									on:change={handleActionChange}
								>
									<option value="" disabled selected>Select an Action</option>
									<option value="changeName">Change Community Name</option>
									<option value="changeDescription">Change Community Description</option>
									<option value="changeCategory">Change Community Category</option>
									<option value="demoteLeader">Demote a Community Leader</option>
									<option value="promoteLeader">Promote User to Community Leader</option>
									<option value="deleteCommunity">Delete Community</option>
								</select>
							</div>
						</div>
						{/if}

					</div>
					{#if selectedAction === 'changeName'}
						<div class="form-control mb-2 flex flex-col gap-3 w-full">
							<div class="w-full">
								<label for="name" class="label">
									<span class="label-text">Got a new name in mind?</span>
								</label>
								<div class="relative flex items-center">
									<input
										type="text"
										bind:value={new_community_name}
										required
										class="input input-bordered validator custom-input"
										placeholder="Type it here..."
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => {
										submit_community_management('name', new_community_name);
									}}>Update</button
								>
							</div>
						</div>
					{/if}
					{#if selectedAction === 'changeDescription'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="name" class="label">
									<span class="label-text">Want to give your community a fresh description?</span>
								</label>
								<div class="relative flex items-center">
									<textarea
										bind:value={new_community_description}
										required
										class="input input-bordered text-area-input"
										placeholder="Type it here..."
										on:input={adjustTextareaHeight}
									/>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => {
										submit_community_management('description', new_community_description);
									}}>Update</button
								>
							</div>
						</div>
					{/if}
					{#if selectedAction === 'changeCategory'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="category" class="label">
									<span class="label-text">Want to change the category?</span>
								</label>
								<div class="relative flex items-center">
									<select
										id="category"
										bind:value={new_community_category}
										required
										class="select select-bordered custom-input flex-grow"
									>
										<option value={null} disabled selected>Pick a new category</option>
										{#each categories as category}
											<option value={category}>{category}</option>
										{/each}
									</select>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={() => {
										submit_community_management('category', new_community_category);
									}}>Update</button
								>
							</div>
						</div>
					{/if}
					{#if selectedAction === 'demoteLeader'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="demoteLeader" class="label">
									<span class="label-text">Need to remove a community leader?</span>
								</label>
								<div class="relative flex items-center">
									<select
										id="demoteLeader"
										bind:value={community_member_to_demote}
										required
										class="select select-bordered custom-input flex-grow"
									>
										{#if community_leaders.length > 0}
											<option value={null} disabled selected>Select a User</option>
										{:else}
											<option value={null} disabled selected>No Users to Select</option>
										{/if}
										{#each community_leaders as member}
											<option value={member.user_id}>{member.username}</option>
										{/each}
									</select>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center text-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									on:click={delete_community_leader}>Update</button
								>
							</div>
						</div>
					{/if}
					{#if selectedAction === 'promoteLeader'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="w-full">
								<label for="promoteLeader" class="label">
									<span class="label-text">Promote User to Community Leader</span>
								</label>
								<div class="relative flex items-center">
									<select
										id="promoteLeader"
										bind:value={community_member_to_promote}
										required
										class="select select-bordered custom-input flex-grow"
									>
										{#if usersList.length > 0}
											<option value={null} disabled selected>Select a User</option>
											{#each usersList as user}
												{#if !community_leaders.some((leader) => leader.user_id === user.value)}
													<option value={user.value}>{user.name}</option>
												{/if}
											{/each}
										{:else}
											<option value={null} disabled selected>No Users Available</option>
										{/if}
									</select>
								</div>
							</div>
							<div class="mb-2 mt-2 flex justify-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									type="submit"
									on:click={add_community_leader}>Update</button
								>
							</div>
						</div>
					{/if}
					{#if selectedAction === 'deleteCommunity'}
						<div class="form-control mb-2 flex flex-col gap-3">
							<div class="mb-2 mt-2 flex justify-center">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
									type="submit"
									on:click={delete_community}>Delete</button
								>
							</div>
						</div>
					{/if}
				</div>
			</div>
			<!-- Community Creation Card -->
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
