<script>
	import { CATEGORIES } from '../../../assets/categories.json';
	import AddIcon from '../../../assets/AddIcon.svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { MultiSelect, Badge } from 'flowbite-svelte';
	import AddIconNoCircle from '../../../assets/AddIconNoCircle.svelte';
	import SettingsIcon from '../../../assets/SettingsIcon.svelte';
	import MediaIcon from '../../../assets/MediaIcon.svelte';

	let categories = [...CATEGORIES.sort((a, b) => a.trim().localeCompare(b.trim())), 'Other']; // Sort the categories alphabetically

	let access_token; // Access token for API authentication
	let name = ''; // Community name
	let description = ''; // Community description
	let category = ''; // Community category
	let customCategory = ''; // Custom category if category is 'Other'
	let community_image = null; // Community image
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
	let new_community_image = null; // New community image for management
	let selected_community_has_image = false; // Flag to check if the selected community has an image
	$: community_leaders = []; // Current members of the selected community
	let community_member_to_demote = null; // Member to demote from leader
	let community_member_to_promote = null; // Member to promote to leader
	let selectedAction = ''; // Variable to store the selected action for community management
	let showCommunityCreateModal = false; // Flag to show/hide the create community modal
	let showCommunityManagementModal = false; // Flag to show/hide the community management modal
	let searchTerm = ''; // Search term for filtering

	// Add reactive statement to filter communities
	$: filteredCommunities = communities.filter(
		(community) =>
			community.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
			(community.description &&
				community.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
			(community.category && community.category.toLowerCase().includes(searchTerm.toLowerCase()))
	);

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

	// Function to handle image selection
	const handleImageChange = (event) => {
		community_image = event.target.files[0];
	};

	// Function to handle image selection for community management
	const handleManagementImageChange = (event) => {
		new_community_image = event.target.files[0];
	};

	const update_community_image = async () => {
		if (!community_management_selected) {
			console.error('No community selected.');
			return;
		}

		if (!new_community_image) {
			alert('Please select an image first.');
			return;
		}

		const confirmation = confirm('Are you sure you want to change the community image?');
		if (!confirmation) return;

		// Create FormData object for file upload
		const formData = new FormData();
		formData.append('community_image', new_community_image);
		formData.append('community_id', community_management_selected);

		try {
			const response = await fetch('http://127.0.0.1:8000/api/community/update_image/', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`
				},
				body: formData
			});
			const result = await response.json();
			if (response.ok) {
				console.log('Community image updated:', result);
				alert('Community image updated successfully!');
				window.location.reload();
			} else {
				alert(result.error || 'Failed to update community image');
				console.error('Error updating community image:', result.error);
			}
		} catch (error) {
			console.error('Network Error:', error.message);
			alert('An error occurred. Please try again!');
		}
	};

	// Function to delete community image
	const delete_community_image = async () => {
		if (!community_management_selected) {
			console.error('No community selected.');
			return;
		}

		const confirmation = confirm('Are you sure you want to remove the community image?');
		if (!confirmation) return;

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/community/${community_management_selected}/delete_image/`,
				{
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);

			const result = await response.json();
			if (response.ok) {
				console.log('Community image deleted:', result);
				alert('Community image removed successfully!');
				window.location.reload();
			} else {
				alert(result.error || 'Failed to remove community image');
				console.error('Error removing community image:', result.error);
			}
		} catch (error) {
			console.error('Network Error:', error.message);
			alert('An error occurred. Please try again!');
		}
	};

	// Function to toggle the community creation modal
	const toggleCommunityCreateModal = () => {
		// Reset the data when the modal is opened
		if (showCommunityCreateModal) {
			name = '';
			description = '';
			category = '';
			customCategory = '';
			selectedUsersForCommunityCreation = [];
			community_image = null;
		}
		showCommunityCreateModal = !showCommunityCreateModal;
	};

	// Function to toggle the community management modal
	const toggleCommunityManagementModal = async (communityId) => {
		community_management_selected = communityId; // Assign the selected community
		if (communityId) {
			await get_community_leaders(); // Fetch the leaders for the selected community

			// Check if the selected community has an image
			const community = communities.find((c) => c.community_id === communityId);
			selected_community_has_image = community ? community.has_image : false;
		}
		showCommunityManagementModal = !showCommunityManagementModal; // Toggle the modal
		selectedAction = ''; // Reset the selected action
		new_community_image = null; // Reset the new community image
	};

	onMount(async () => {
		try {
			// Retrieve the access_token from localStorage
			access_token = localStorage.getItem('access_token');

			// If there's no access_token, redirect to the login page or home
			if (!access_token) {
				goto('http://localhost:5173/'); // Or wherever you want the user to go if they are not logged in
				return;
			}

			// Decode the logged-in user's ID from the token
			loggedInUserId = getLoggedInUserIdFromToken(access_token);

			// Fetch users and subscribed communities
			await fetchUsers();
			await fetchSubscribedCommunities();

			// Fetch all communities
			const response = await fetch('http://127.0.0.1:8000/api/communities/');
			if (!response.ok) {
				throw new Error(`HTTP error! Status: ${response.status}`);
			}
			const data = await response.json();
			communities = data;
		} catch (error) {
			console.error('Error during initialization:', error);
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

	// submit form to create a new community
	const submitForm = async (event) => {
		event.preventDefault();
		// checks if all fields are completed if not it will not submit
		if (!name || !description || !category) {
			console.log('All fields are required!');
			return;
		}

		const confirmation = confirm('Are you sure?');
		if (!confirmation) return;

		// Create FormData object for file upload
		const formData = new FormData();
		formData.append('name', name);
		formData.append('description', description);
		formData.append('category', category === 'Other' ? customCategory : category);

		// Add leader_ids as a JSON string
		if (selectedUsersForCommunityCreation.length > 0) {
			formData.append('leader_ids', JSON.stringify(selectedUsersForCommunityCreation));
		}

		// Add the image file if it exists
		if (community_image) {
			formData.append('community_image', community_image);
		}

		// the api call and post method
		try {
			const response = await fetch('http://127.0.0.1:8000/api/create_community/', {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${access_token}`
				},
				body: formData
			});

			const result = await response.json();
			// if it worked and is okay display in the console log the data passed through and then reload the window
			if (response.ok) {
				console.log('Community created:', result);
				name = '';
				description = '';
				category = '';
				selectedUsersForCommunityCreation = [];
				community_image = null;
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
			const response = await fetch(`http://127.0.0.1:8000/api/leave_community/${communityId}/`, {
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
				await fetchSubscribedCommunities();
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

<main class="px-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<!-- Top panel with search bar -->
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>

	<!-- Community Creation Modal -->
	{#if showCommunityCreateModal}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
			on:click={toggleCommunityCreateModal}
		>
			<div
				class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-3xl"
				on:click|stopPropagation
			>
				<h1 class="text-primary mb-6 text-center text-4xl font-bold">Create Community</h1>
				<form id="community-form" class="space-y-4" on:submit|preventDefault={submitForm}>
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
									class="select select-bordered validator custom-input placeholder-selected"
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
					<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
						<div class="w-full">
							<label for="name" class="label">
								<span class="label-text wrap">Community Leaders(Optional)</span>
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

					<!-- In the community creation modal form, add this section after the category section: -->
					<div class="form-control mb-5 flex flex-col gap-3 sm:flex-row">
						<div class="w-full">
							<label for="community-image" class="label">
								<span class="label-text">Community Image (Optional)</span>
							</label>
							<div class="relative">
								<!-- Image Preview -->
								{#if community_image}
									<div class="mb-3 flex justify-center">
										<img
											src={URL.createObjectURL(community_image)}
											alt="Selected Image"
											class="rounded-md min-w-[20%] max-w-[25%] h-auto"
										/>
									</div>
								{/if}
								<!-- Image Upload Widget -->
								<div class="tooltip-container">
									<label
										for="community-file-upload"
										class="ml-2 cursor-pointer flex items-center text-base-100 hover:text-primary"
									>
										<MediaIcon size={28} />
									</label>
									<!-- Hidden File Input -->
									<input
										id="community-file-upload"
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleImageChange}
									/>
									<span class="tooltip">Add Media</span>
								</div>
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
	{/if}

	<!--Community Management Model-->
	{#if showCommunityManagementModal}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
			on:click={() => toggleCommunityManagementModal(null)}
		>
			<div
				class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-3xl"
				on:click|stopPropagation
			>
				<h1 class="text-primary mb-6 text-center text-4xl font-bold">
					Manage Community: {communities.find(
						(c) => c.community_id === community_management_selected
					)?.name}
				</h1>
				<div class="form-control mb-2 flex flex-col gap-3">
					<label for="action" class="label">
						<span class="label-text">What would you like to do?</span>
					</label>
					<div class="relative flex items-center">
						<select
							id="action"
							bind:value={selectedAction}
							required
							class="select select-bordered custom-input flex-grow placeholder-selected"
							on:change={handleActionChange}
						>
							<option value="" disabled selected>Select an Action</option>
							<option value="changeName">Change Community Name</option>
							<option value="changeDescription">Change Community Description</option>
							<option value="changeCategory">Change Community Category</option>
							<option value="promoteLeader">Promote User to Community Leader</option>
							<option value="demoteLeader">Demote a Community Leader</option>
							{#if selected_community_has_image}
								<option value="changeImage">Change Community Image</option>
								<option value="deleteImage">Delete Community Image</option>
							{:else}
								<option value="addImage">Add Community Image</option>
							{/if}
							<option value="deleteCommunity">Delete Community</option>
						</select>
					</div>
				</div>
				<!--Change the community name-->
				{#if selectedAction === 'changeName'}
					<div class="form-control mb-2 flex flex-col gap-3">
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
				<!--Change the community description -->
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
				<!--Change the community category -->
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
									class="select select-bordered custom-input flex-grow placeholder-selected"
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
				<!--Demote a community leader-->
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
									class="select select-bordered custom-input flex-grow placeholder-selected"
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
								on:click={delete_community_leader}>Demote</button
							>
						</div>
					</div>
				{/if}
				<!-- Promote a community leader -->
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
									class="select select-bordered custom-input flex-grow placeholder-selected"
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
								on:click={add_community_leader}>Promote</button
							>
						</div>
					</div>
				{/if}

				<!-- Change Community Image -->
				{#if selectedAction === 'changeImage' && selected_community_has_image}
					<div class="form-control mb-2 flex flex-col gap-3">
						<div class="w-full">
							<label for="community-image-update" class="label">
								<span class="label-text">Upload a new community image</span>
							</label>
							<div class="relative">
								<!-- Image Preview -->
								{#if new_community_image}
									<div class="mb-3 flex justify-center">
										<img
											src={URL.createObjectURL(new_community_image)}
											alt="Selected Image"
											class="rounded-md min-w-[20%] max-w-[50%] h-auto"
										/>
									</div>
								{/if}

								<!-- File Input -->
								<div class="flex items-center gap-2">
									<label
										for="community-management-file-upload"
										class="ml-2 cursor-pointer flex items-center gap-2 text-base-100 hover:text-primary"
									>
										<MediaIcon size={28} />
									</label>
									<input
										id="community-management-file-upload"
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleManagementImageChange}
									/>
								</div>
							</div>
						</div>
						<div class="mb-2 mt-2 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								on:click={update_community_image}
								disabled={!new_community_image}
							>
								Update
							</button>
						</div>
					</div>
				{/if}

				<!-- Delete Community Image (when image exists) -->
				{#if selectedAction === 'deleteImage' && selected_community_has_image}

						<div class="mb-2 mt-2 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								on:click={delete_community_image}
							>
								Delete
							</button>
						</div>

				{/if}

				<!-- Add Community Image (when no image exists) -->
				{#if selectedAction === 'addImage' && !selected_community_has_image}
					<div class="form-control mb-2 flex flex-col gap-3">
						<div class="w-full">
							<label for="community-image-add" class="label">
								<span class="label-text">Upload a community image</span>
							</label>
							<div class="relative">
								<!-- Image Preview -->
								{#if new_community_image}
									<div class="mb-3 flex justify-center">
										<img
											src={URL.createObjectURL(new_community_image)}
											alt="Selected Image"
											class="rounded-md max-w-[50%] h-auto"
										/>
									</div>
								{/if}

								<!-- File Input -->
								<div class="flex items-center gap-2">
									<label
										for="community-management-file-upload"
										class="ml-2 cursor-pointer flex items-center gap-2 text-base-100 hover:text-primary"
									>
										<MediaIcon size={28} />
									</label>
									<input
										id="community-management-file-upload"
										type="file"
										accept="image/*"
										class="hidden"
										on:change={handleManagementImageChange}
									/>
								</div>
							</div>
						</div>
						<div class="mb-2 mt-2 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								on:click={update_community_image}
								disabled={!new_community_image}
							>
								Add Image
							</button>
						</div>
					</div>
				{/if}

				<!-- Delete the community -->
				{#if selectedAction === 'deleteCommunity'}
						<div class="mb-2 mt-2 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
								type="submit"
								on:click={delete_community}>Delete</button
							>
						</div>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Main Section -->
	<div class="gap-6 grid w-full max-w-full grid-cols-1 justify-center md:grid-cols-3">
		<!-- List Communities and Join Button -->
		{#each filteredCommunities as community}
			<div class="card bg-base-100 w-full rounded-3xl">
				<!-- Community Image -->
				{#if community.has_image}
					<figure class="h-48 w-full">
						{#await fetch(`http://127.0.0.1:8000/api/community/${community.community_id}/image/`).then( (r) => r.json() ) then imageData}
							<img
								src={imageData.image}
								alt={community.name}
								class="w-full h-full object-contain bg-gray-200"
							/>
						{:catch}
							<div class="flex items-center justify-center w-full h-full bg-gray-200">
								<MediaIcon size={48} class="text-gray-400" />
							</div>
						{/await}
					</figure>
				{:else}
					<figure class="bg-gray-200 h-48 flex items-center justify-center">
						<span class="text-gray-400">No image available</span>
					</figure>
				{/if}
				<div class="card-body bg-secondary rounded-b-3xl">
					<div class="card-title flex justify-between">
						<h2 class="text-primary text-2xl font-bold truncate">{community.name}</h2>

						<div class="flex gap-2">
							<!-- Show "Manage" button if the user is the owner of the community-->
							{#if community.owner_id === loggedInUserId}
								<div class="tooltip-container">
									<button
										on:click={() => toggleCommunityManagementModal(community.community_id)}
										class="hover:text-primary"
										aria-label="Manage Community"
									>
										<SettingsIcon />
									</button>
									<span class="tooltip">Manage this community</span>
								</div>
							{/if}
							<!-- Show "Leave" button if the user is subscribed and not the owner of the community -->
							{#if subscribedCommunities.some((sub) => sub.id === community.community_id) && community.owner_id != loggedInUserId}
								<div class="tooltip-container">
									<button
										on:click={() => leave_community(community.community_id)}
										class="hover:text-primary"
										aria-label="Leave Community"
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
									<span class="tooltip">Leave this community</span>
								</div>
								<!-- Show "Join" button if the user is not subscribed, or leader or owner -->
							{:else if !subscribedCommunities.some((sub) => sub.id === community.community_id)}
								<div class="tooltip-container">
									<button
										on:click={() => join_community(community.community_id)}
										class="hover:text-primary"
									>
										<AddIcon />
									</button>
									<span class="tooltip">Join this community</span>
								</div>
							{/if}
						</div>
					</div>

					<!-- Community description -->
					<p class="community-description">{community.description}</p>

					<!-- Category badges at bottom -->
					<div class="card-actions justify-end mt-2">
						<div class="badge badge-outline">{community.category}</div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Floating Add Button -->
	<button
		class="fixed bottom-5 right-5 bg-primary text-secondary p-4 rounded-full shadow-lg hover:bg-primary-focus z-50"
		on:click={toggleCommunityCreateModal}
	>
		<AddIconNoCircle size={28} />
	</button>
</main>
