<script lang="ts">
	import { onMount } from 'svelte';
	import { CATEGORIES } from '../../../assets/categories.json';
	import AddIcon from '../../../assets/AddIcon.svelte';
	import EditIcon from '../../../assets/EditIcon.svelte';
	import ShowPasswordIcon from '../../../assets/ShowPasswordIcon.svelte';
	import { page } from '$app/stores';
	import {
		fetchUserProfile,
		type UserProfile,
		updateProfilePicture,
		updateProfile,
		updateSocialMedia,
		removeSocialMedia,
		socialMedias,
		updateAbout,
		updateInterests
	} from '$lib/api/profile';
	import { changePassword } from '$lib/api/password';
	import RemoveIcon from '../../../assets/RemoveIcon.svelte';

	let categories = [...CATEGORIES.sort((a, b) => a.trim().localeCompare(b.trim())), 'Other']; // Sort the categories alphabetically
	let searchTerm = ''; // Search term for filtering

	// Fetch the user profile from the API
	let userProfile: UserProfile = {
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

	// Initialise variables for profile editing
	let showCurrentPassword = false;
	let showNewPassword = false;
	let showConfirmPassword = false;
	let isUploading = false;
	let isChangingPassword = false;
	let isUpdatingProfile = false;
	let currentPassword = '';
	let newPassword = '';
	let confirmPassword = '';
	let isEditingProfile = false;
	let editedProfile = {
		username: '',
		first_name: '',
		last_name: '',
		email: ''
	};

	let tempProfilePicture = ''; // Temporary variable for profile picture upload

	// Social media section editing
	let isAddingSocial = false;
	let selectedSocialType = '';
	let socialUsername = '';
	let isUpdatingSocial = false;

	// About section editing
	let isEditingAbout = false;
	let editedAbout = '';
	let isUpdatingAbout = false;

	// Interests section editing
	let isEditingInterests = false;
	let isUpdatingInterests = false;
	let newInterest = '';
	let editedInterests: string[] = []; // Define editedInterests as an array

	// Function to handle profile picture upload
	async function handleProfilePictureUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files || !input.files[0]) return;

		try {
			isUploading = true;
			const file = input.files[0];
			const reader = new FileReader();

			reader.onload = async (e) => {
				const base64Image = e.target?.result as string;
				tempProfilePicture = base64Image;
			};

			reader.onerror = () => {
				alert('Failed to read the image file');
			};

			reader.readAsDataURL(file);
		} catch (error) {
			console.error('Failed to upload profile picture:', error);
			alert('Failed to upload profile picture. Please try again.');
		} finally {
			isUploading = false;
		}
	}

	// Function to handle password change
	async function handlePasswordChange(event: Event) {
		event.preventDefault();

		// validate passwords match
		if (newPassword !== confirmPassword) {
			alert('New passwords do not match!');
			return;
		}

		try {
			isChangingPassword = true;

			await changePassword(currentPassword, newPassword);
			alert('Password changed successfully!');

			// clear form
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (error) {
			console.error('Failed to change password:', error);
			let errorMessage = error instanceof Error ? error.message : 'Failed to change password';
			alert(errorMessage + '. Please try again!');
		} finally {
			isChangingPassword = false;
		}
	}

	// Function to handle profile update
	async function handleProfileUpdate(event: Event) {
		event.preventDefault();

		try {
			isUpdatingProfile = true;

			// Update the profile picture if a new one was uploaded
			if (tempProfilePicture) {
				await updateProfilePicture(tempProfilePicture);
				userProfile.profile_picture = tempProfilePicture; // Save the uploaded image
				tempProfilePicture = ''; // Clear the temporary variable
			}

			await updateProfile(editedProfile);
			// update local profile data
			userProfile.username = editedProfile.username;
			userProfile.first_name = editedProfile.first_name;
			userProfile.last_name = editedProfile.last_name;
			userProfile.email = editedProfile.email;
			isEditingProfile = false;
		} catch (error) {
			console.error('Failed to update profile:', error);
			let errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
			alert(errorMessage + '. Please try again!');
		} finally {
			isUpdatingProfile = false;
		}
	}

	// Function to start editing profile
	function startEditingProfile() {
		editedProfile = {
			username: userProfile.username,
			first_name: userProfile.first_name,
			last_name: userProfile.last_name,
			email: userProfile.email
		};
		isEditingProfile = true;
	}

	// Function to cancel editing profile
	function cancelEditingProfile() {
		isEditingProfile = false;
		tempProfilePicture = ''; // Clear the temporary image
	}

	// Function to handle social media addition
	async function handleAddSocial(event: Event) {
		event.preventDefault();

		if (!selectedSocialType || !socialUsername) {
			alert('Please select a social media type and enter a username!');
			return;
		}

		try {
			isUpdatingSocial = true;

			await updateSocialMedia(selectedSocialType, socialUsername);

			// refresh profile data
			userProfile = await fetchUserProfile();
			isAddingSocial = false;
			selectedSocialType = '';
			socialUsername = '';
		} catch (error) {
			console.error('Failed to add social media:', error);
			let errorMessage = error instanceof Error ? error.message : 'Failed to add social media';
			alert(errorMessage + '. Please try again!');
		} finally {
			isUpdatingSocial = false;
		}
	}

	// Function to handle social media removal
	async function handleRemoveSocial(socialType: string) {
		try {
			isUpdatingSocial = true;

			await removeSocialMedia(socialType);

			// refresh profile data
			userProfile = await fetchUserProfile();
		} catch (error) {
			console.error('Failed to remove social media:', error);
			let errorMessage = error instanceof Error ? error.message : 'Failed to remove social media';
			alert(errorMessage + '. Please try again!');
		} finally {
			isUpdatingSocial = false;
		}
	}

	// Function to start editing about section
	function startEditingAbout() {
		editedAbout = userProfile?.about || '';
		isEditingAbout = true;
	}

	// Function to handle about section update
	function cancelEditingAbout() {
		isEditingAbout = false;
		editedAbout = '';
	}

	// Function to handle about section update
	async function handleAboutUpdate() {
		isUpdatingAbout = true;

		try {
			const result = await updateAbout(editedAbout);
			userProfile = { ...userProfile, about: result.about };
			isEditingAbout = false;
		} catch (error) {
			let errorMessage = error instanceof Error ? error.message : 'Failed to update about section';
			alert(errorMessage + '. Please try again!');
		} finally {
			isUpdatingAbout = false;
		}
	}

	// Function to cancel editing interests
	function cancelEditingInterests() {
		isEditingInterests = false;
		newInterest = '';
	}

	// Function to handle adding a new interest
	async function addInterest(event: Event) {
		event.preventDefault();

		if (!newInterest) {
			alert('Please select an interest!');
			return;
		}

		try {
			isUpdatingInterests = true;

			// TODO: John -> this should be adding the interest to the backend

			// Add the new interest to the list
			editedInterests = [...editedInterests, newInterest]; // TODO: John -> this won't be necessary, for the dropdown under interests section, user shouldn't see the the interest that they already have which comes from the database

			//TODO: John -> Think as the same way as the social media section, we are not creating a new list in the page as socialMedias we are handling on the backend

			// Update the backend
			const result = await updateInterests(editedInterests);

			// Update the user profile
			userProfile = { ...userProfile, interests: result.interests };

			// Reset the form
			newInterest = '';
			isEditingInterests = false;
		} catch (error) {
			console.error('Failed to add interest:', error);
      let errorMessage = error instanceof Error ? error.message : 'Failed to update interests';
			alert(errorMessage + '. Please try again!');
		} finally {
			isUpdatingInterests = false;
		}
	}

	// Function to handle removing an interest
	function removeInterest(index: number) {
		editedInterests = editedInterests.filter((_, i) => i !== index);
		// TODO: To John -> this should be removed from UserInterest in the backend instead of edited Interests?
	}

	onMount(async () => {
		try {
			userProfile = await fetchUserProfile();
		} catch (error) {
			console.error('Failed to fetch user profile:', error);
		}
	});
</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	<!-- Top panel with search bar -->
	<div class="top-panel">
		<input type="text" placeholder="Search..." class="input search-bar" bind:value={searchTerm} />
	</div>
	<!-- Main content area -->
	<div
		class="gap-13 flex grid w-full max-w-full grid-cols-1 flex-col justify-center md:grid-cols-2"
	>
		<!-- Left Column -->
		<div class="space-y-10">
			<!-- Profile Section -->
			<div class="card bg-base-100 min-h-1/2 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="flex flex-end justify-end">
						<div class="tooltip-container">
							<button
								class="hover:text-primary flex items-center"
								style="visibility: {isEditingProfile ? 'hidden' : 'visible'};"
								on:click={isEditingProfile ? cancelEditingProfile : startEditingProfile}
							>
								<EditIcon />
								<span class="tooltip" style="visibility: {isEditingProfile ? 'hidden' : 'visible'};"
									>Edit details</span
								>
							</button>
						</div>
					</div>
					<!-- Profile Image Container -->
					<div class="flex flex-col items-center">
						<div class="relative w-50 h-50 mb-5">
							<!-- Profile Image or Placeholder -->
							{#if tempProfilePicture || userProfile.profile_picture}
								<img
									src={tempProfilePicture || userProfile.profile_picture}
									alt="Profile Picture"
									class="h-full w-full object-cover rounded-full"
								/>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 338 338"
									fill="#DDD"
									class="h-full w-full object-cover object-center rounded-full"
								>
									<path
										d="m169,.5a169,169 0 1,0 2,0zm0,86a76,76 0 1 1-2,0zM57,287q27-35 67-35h92q40,0 67,35a164,164 0 0,1-226,0"
									/>
								</svg>
							{/if}
							<!-- Text Overlay -->
							{#if isEditingProfile}
								<div class="w-50 h-50 upload-button">
									<label class="flex items-center justify-center cursor-pointer" for="file-upload">
										<svg
											class="size-12"
											aria-hidden="true"
											xmlns="http://www.w3.org/2000/svg"
											fill="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												fill-rule="evenodd"
												d="M13 10a1 1 0 0 1 1-1h.01a1 1 0 1 1 0 2H14a1 1 0 0 1-1-1Z"
												clip-rule="evenodd"
											/>
											<path
												fill-rule="evenodd"
												d="M2 6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v12c0 .556-.227 1.06-.593 1.422A.999.999 0 0 1 20.5 20H4a2.002 2.002 0 0 1-2-2V6Zm6.892 12 3.833-5.356-3.99-4.322a1 1 0 0 0-1.549.097L4 12.879V6h16v9.95l-3.257-3.619a1 1 0 0 0-1.557.088L11.2 18H8.892Z"
												clip-rule="evenodd"
											/>
										</svg>
									</label>
									<!-- Hidden File Input -->
									<input
										id="file-upload"
										type="file"
										accept="image/*"
										class="absolute inset-0 opacity-0 cursor-pointer"
										on:change={handleProfilePictureUpload}
										disabled={isUploading}
									/>
								</div>
							{/if}
						</div>
						<!-- Profile Information Section -->
						<div class="w-full">
							<div class="mb-2 flex justify-between items-center">
								<label for="user_name" class="label text-primary">
									<p class="label-text">Username:</p>
								</label>
								{#if isEditingProfile}
									<div>
										<input
											type="text"
											id="username"
											bind:value={editedProfile.username}
											class="input input-bordered validator custom-input-profile"
											required
											pattern="[A-Za-z][A-Za-z0-9\-_]*"
											minlength="3"
											maxlength="30"
										/>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.username}</p>
								{/if}
							</div>
							<div class="mb-2 flex justify-between items-center">
								<label for="name" class="label text-primary">
									<p class="label-text">Name:</p>
								</label>
								{#if isEditingProfile}
									<div class="flex flex-col ml-2">
										<div class="flex gap-2">
											<div class="flex flex-col ml-auto justify-center">
												<input
													type="text"
													id="first_name"
													bind:value={editedProfile.first_name}
													class="input input-bordered validator custom-input-profile"
													required
													pattern="[A-Za-z]+"
													minlength="1"
												/>
											</div>
											<div class="flex flex-col ml-auto justify-center">
												<input
													type="text"
													id="last_name"
													bind:value={editedProfile.last_name}
													class="input input-bordered validator custom-input-profile"
													required
													pattern="[A-Za-z]+"
												/>
											</div>
										</div>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.first_name} {userProfile.last_name}</p>
								{/if}
							</div>
							<div class="mb-2 flex justify-between items-center">
								<label for="email" class="label text-primary">
									<p class="label-text">Email:</p>
								</label>
								{#if isEditingProfile}
									<div class="ml-auto justify-center">
										<input
											type="email"
											id="email"
											bind:value={editedProfile.email}
											class="input input-bordered validator custom-input-profile"
											required
										/>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.email}</p>
								{/if}
							</div>
							<div class="flex justify-end gap-2 mt-4" class:invisible={!isEditingProfile}>
								<button
									class="btn btn-ghost"
									on:click={cancelEditingProfile}
									disabled={isUpdatingProfile}
								>
									Cancel
								</button>
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
									on:click={handleProfileUpdate}
									disabled={isUpdatingProfile}
								>
									{#if isUpdatingProfile}
										<span class="loading loading-spinner loading-xs"></span>
										Updating...
									{:else}
										Save
									{/if}
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
			<!-- Change Password Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/2 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">Change Password</h1>
					<form class="space-y-3" on:submit={handlePasswordChange}>
						<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="current_password" class="label">
									<span class="label-text">Current Password</span>
								</label>
								<div class="relative">
									<input
										type={showCurrentPassword ? 'text' : 'password'}
										name="current_password"
										bind:value={currentPassword}
										class="input input-bordered validator custom-input pr-9"
										required
										minlength="8"
										autocomplete="current-password"
										placeholder="Enter your current password"
									/>
									<button
										type="button"
										class="absolute inset-y-0 right-0 flex items-center pb-6 pr-3 text-sm leading-5"
										on:click={() => (showCurrentPassword = !showCurrentPassword)}
									>
										{#if showCurrentPassword}
											<ShowPasswordIcon />
										{:else}
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="size-5"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
												/>
											</svg>
										{/if}
									</button>
									<p class="validator-hint">Must be more than 8 characters!</p>
								</div>
							</div>
						</div>
						<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
							<div class="w-full">
								<label for="new_password" class="label">
									<span class="label-text">New Password</span>
								</label>
								<div class="relative">
									<input
										type={showNewPassword ? 'text' : 'password'}
										name="new_password"
										bind:value={newPassword}
										class="input input-bordered validator custom-input pr-9"
										required
										minlength="8"
										autocomplete="new-password"
										placeholder="Enter your new password"
									/>
									<button
										type="button"
										class="absolute inset-y-0 right-0 flex items-center pb-6 pr-3 text-sm leading-5"
										on:click={() => (showNewPassword = !showNewPassword)}
									>
										{#if showNewPassword}
											<ShowPasswordIcon />
										{:else}
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="size-5"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
												/>
											</svg>
										{/if}
									</button>
									<p class="validator-hint">Must be more than 8 characters!</p>
								</div>
							</div>
						</div>
						<div class="form-control flex flex-col gap-3 sm:flex-row mb-0">
							<div class="w-full">
								<label for="confirm_password" class="label">
									<span class="label-text">Confirm Password</span>
								</label>
								<div class="relative">
									<input
										type={showConfirmPassword ? 'text' : 'password'}
										name="confirm_password"
										bind:value={confirmPassword}
										class="input input-bordered validator custom-input pr-9"
										required
										minlength="8"
										autocomplete="new-password"
										placeholder="Confirm your new password"
									/>
									<button
										type="button"
										class="absolute inset-y-0 right-0 flex items-center pb-6 pr-3 text-sm leading-5"
										on:click={() => (showConfirmPassword = !showConfirmPassword)}
									>
										{#if showConfirmPassword}
											<ShowPasswordIcon />
										{:else}
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="size-5"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88"
												/>
											</svg>
										{/if}
									</button>
									<p class="validator-hint">Must be more than 8 characters!</p>
								</div>
							</div>
						</div>
						<div class="form-control flex justify-center mt-3 mb-0">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
								type="submit"
								disabled={isChangingPassword}
							>
								{#if isChangingPassword}
									<span class="loading loading-spinner loading-xs"></span>
									Changing...
								{:else}
									Confirm
								{/if}
							</button>
						</div>
					</form>
				</div>
			</div>
		</div>

		<!-- Right Column -->
		<div class="space-y-10">
			<!-- About Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">About</h1>
						</div>
						<div class="tooltip-container">
							<button
								class="hover:text-primary"
								style="visibility: {isEditingAbout ? 'hidden' : 'visible'};"
								on:click={isEditingAbout ? cancelEditingAbout : startEditingAbout}
							>
								<EditIcon />
								<span class="tooltip" style="visibility: {isEditingAbout ? 'hidden' : 'visible'};"
									>Edit bio</span
								>
							</button>
						</div>
					</div>
					{#if isEditingAbout}
						<div class="form-control mb-2 flex flex-col gap-3 w-full">
							<textarea
								bind:value={editedAbout}
								rows="5"
								class="input input-bordered text-area-input"
								placeholder="Tell us about yourself..."
							></textarea>
							<div class="flex justify-end space-x-3">
								<button
									on:click={cancelEditingAbout}
									class="btn btn-ghost"
									disabled={isUpdatingAbout}
								>
									Cancel
								</button>
								<button
									on:click={handleAboutUpdate}
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
									disabled={isUpdatingAbout}
								>
									{#if isUpdatingAbout}
										<span class="loading loading-spinner loading-xs"></span>
										Updating...
									{:else}
										Save
									{/if}
								</button>
							</div>
						</div>
					{:else}
						<p class="text-user-details whitespace-pre-wrap">
							{userProfile?.about || 'No bio available.'}
						</p>
					{/if}
				</div>
			</div>
			<!-- Socials Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">Socials</h1>
						</div>
						<div class="tooltip-container">
							<button
								on:click={() => (isAddingSocial = true)}
								class="hover:text-primary"
								style="visibility: {isAddingSocial ? 'hidden' : 'visible'};"
							>
								<AddIcon />
							</button>
							<span class="tooltip" style="visibility: {isAddingSocial ? 'hidden' : 'visible'};"
								>Connect social media account</span
							>
						</div>
					</div>
					{#if isAddingSocial}
						<form class="form-control mb-2 flex flex-col gap-3" on:submit={handleAddSocial}>
							<div class="w-full">
								<label class="label">
									<span class="label-text">Select Social Media</span>
								</label>
								<div class="relative flex items-center">
									<select
										class="select select-bordered custom-input flex-grow"
										bind:value={selectedSocialType}
										required
									>
										<option value="">Choose a platform</option>
										{#each socialMedias.sort((a, b) => a.name.localeCompare(b.name)) as social}
											{#if !userProfile.social_type.includes(social.name)}
												<option value={social.name}>
													{social.name.charAt(0).toUpperCase() + social.name.slice(1)}
												</option>
											{/if}
										{/each}
									</select>
								</div>
							</div>
							<div class="form-control flex flex-col gap-3">
								<div class="w-full">
									<label class="label">
										<span class="label-text">Username</span>
									</label>
									<div class="relative flex items-center">
										<input
											type="text"
											class="input input-bordered validator custom-input"
											bind:value={socialUsername}
											required
											placeholder="What's your username?"
										/>
									</div>
								</div>
							</div>
							<div class="flex justify-end gap-2">
								<button
									type="button"
									class="btn btn-ghost"
									on:click={() => {
										isAddingSocial = false;
										selectedSocialType = '';
										socialUsername = '';
									}}
									disabled={isUpdatingSocial}
								>
									Cancel
								</button>
								<button
									type="submit"
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
									disabled={isUpdatingSocial}
								>
									{#if isUpdatingSocial}
										<span class="loading loading-spinner loading-xs"></span>
										Adding...
									{:else}
										Add
									{/if}
								</button>
							</div>
						</form>
					{:else if userProfile.social_type.length === 0}
						<!-- Message when no social media is found -->
						<div class="flex flex-wrap justify-center space-y-2">
							<p class="text-user-details text-center">No socials connected yet.</p>
						</div>
					{:else}
						<div class="flex flex-wrap justify-center space-y-2">
							<!-- Loop through social media accounts -->
							{#each userProfile.social_type as type, index}
								{#each socialMedias as social (social.name)}
									{#if social.name === type}
										<div class="border-base-100 m-1 flex space-x-2 rounded-lg border-2 p-2">
											<div>{@html social.svg}</div>
											<p class="text-user-details pr-2">{userProfile.social_username[index]}</p>
											<button
												class="hover:text-primary"
												on:click={() => handleRemoveSocial(type)}
												disabled={isUpdatingSocial}
											>
												<RemoveIcon />
											</button>
										</div>
									{/if}
								{/each}
							{/each}
						</div>
					{/if}
				</div>
			</div>
			<!-- Interests Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">Interests</h1>
						</div>
						<div class="tooltip-container">
							<button
								on:click={() => (isEditingInterests = true)}
								class="hover:text-primary"
								style="visibility: {isEditingInterests ? 'hidden' : 'visible'};"
							>
								<AddIcon />
							</button>
							<span class="tooltip" style="visibility: {isEditingInterests ? 'hidden' : 'visible'};"
								>Add interest</span
							>
						</div>
					</div>

					{#if isEditingInterests}
						<!-- Form to Add Interests -->
						<form class="form-control mb-2 flex flex-col gap-3" on:submit={addInterest}>
							<div class="w-full">
								<label class="label">
									<span class="label-text">Select an interest</span>
								</label>
								<div class="relative flex items-center">
									<select
										class="select select-bordered custom-input flex-grow"
										bind:value={newInterest}
										required
									>
										<option value="" disabled selected>Pick a hobby</option>
										{#each categories as category}
											{#if !editedInterests.includes(category)}
												<option value={category}>{category}</option>
											{/if}
										{/each}
									</select>
								</div>
							</div>
							<div class="flex justify-end gap-2">
								<button
									type="button"
									class="btn btn-ghost"
									on:click={cancelEditingInterests}
									disabled={isUpdatingInterests}
								>
									Cancel
								</button>
								<button
									type="submit"
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
									disabled={isUpdatingInterests}
								>
									{#if isUpdatingInterests}
										<span class="loading loading-spinner loading-xs"></span>
										Adding...
									{:else}
										Add
									{/if}
								</button>
							</div>
						</form>
					{:else if userProfile?.interests.length === 0}
						<!-- Message when no interests are found -->
						<div class="flex flex-wrap justify-center space-y-2">
							<p class="text-user-details text-center">No interests added yet.</p>
						</div>
					{:else}
						<!-- Display Interests -->
						<div class="flex flex-wrap justify-center space-y-2">
							{#each userProfile.interests as interest, index}
								<div class="border-base-100 m-1 flex space-x-2 rounded-lg border-2 p-2">
									<p class="text-user-details pr-2">{interest}</p>
									<button
										class="hover:text-primary"
										on:click={() => removeInterest(index)}
										disabled={isUpdatingInterests}
									>
										<RemoveIcon />
									</button>
								</div>
							{/each}

						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</main>
