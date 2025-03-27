<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { fetchUserProfile, type UserProfile, updateProfilePicture, updateProfile, updateSocialMedia, removeSocialMedia, socialMedias, updateAbout, updateInterests } from '$lib/api/profile';
	import { changePassword } from '$lib/api/password';

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

	let showCurrentPassword = false;
	let showNewPassword = false;
	let showConfirmPassword = false;
	let errorMessage: string | null = null;
	let successMessage: string | null = null;
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

	let pencil =
		'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-8"><path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" /></svg>';

	let validationErrors = {
		username: '',
		first_name: '',
		last_name: '',
		email: ''
	};

	let isAddingSocial = false;
	let selectedSocialType = '';
	let socialUsername = '';
	let isUpdatingSocial = false;

	let isEditingAbout = false;
	let editedAbout = '';
	let isUpdatingAbout = false;
	let aboutError = '';

	let isEditingInterests = false;
	let editedInterests: string[] = [];
	let isUpdatingInterests = false;
	let interestsError = '';
	let newInterest = '';

	function validateProfile() {
		validationErrors = {
			username: '',
			first_name: '',
			last_name: '',
			email: ''
		};
		let isValid = true;

		// Username validation
		if (!editedProfile.username) {
			validationErrors.username = 'Username is required';
			isValid = false;
		} else if (!/^[a-zA-Z0-9]{3,30}$/.test(editedProfile.username)) {
			validationErrors.username = 'Username must be 3-30 characters long and contain only letters and numbers';
			isValid = false;
		}

		// First name validation
		if (!editedProfile.first_name) {
			validationErrors.first_name = 'First name is required';
			isValid = false;
		} else if (!/^[a-zA-Z]{2,}$/.test(editedProfile.first_name)) {
			validationErrors.first_name = 'First name must be at least 2 characters long and contain only letters';
			isValid = false;
		}

		// Last name validation
		if (!editedProfile.last_name) {
			validationErrors.last_name = 'Last name is required';
			isValid = false;
		} else if (!/^[a-zA-Z]{2,}$/.test(editedProfile.last_name)) {
			validationErrors.last_name = 'Last name must be at least 2 characters long and contain only letters';
			isValid = false;
		}

		// Email validation
		if (!editedProfile.email) {
			validationErrors.email = 'Email is required';
			isValid = false;
		} else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(editedProfile.email)) {
			validationErrors.email = 'Please enter a valid email address';
			isValid = false;
		}

		return isValid;
	}

	async function handleProfilePictureUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files || !input.files[0]) return;

		try {
			isUploading = true;
			errorMessage = null;
			successMessage = null;

			const file = input.files[0];
			const reader = new FileReader();

			reader.onload = async (e) => {
				const base64Image = e.target?.result as string;
				await updateProfilePicture(base64Image);
				userProfile.profile_picture = base64Image;
				successMessage = 'Profile picture updated successfully!';
			};

			reader.onerror = () => {
				errorMessage = 'Failed to read the image file';
			};

			reader.readAsDataURL(file);
		} catch (error) {
			console.error('Failed to upload profile picture:', error);
			errorMessage = 'Failed to upload profile picture. Please try again.';
		} finally {
			isUploading = false;
		}
	}

	async function handlePasswordChange(event: Event) {
		event.preventDefault();
		
		// validate passwords match
		if (newPassword !== confirmPassword) {
			errorMessage = 'New passwords do not match';
			return;
		}

		try {
			isChangingPassword = true;
			errorMessage = null;
			successMessage = null;

			await changePassword(currentPassword, newPassword);
			successMessage = 'Password changed successfully!';
			
			// clear form
			currentPassword = '';
			newPassword = '';
			confirmPassword = '';
		} catch (error) {
			console.error('Failed to change password:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to change password';
		} finally {
			isChangingPassword = false;
		}
	}

	async function handleProfileUpdate(event: Event) {
		event.preventDefault();
		
		if (!validateProfile()) {
			errorMessage = 'Please fix the validation errors before submitting';
			return;
		}
		
		try {
			isUpdatingProfile = true;
			errorMessage = null;
			successMessage = null;

			await updateProfile(editedProfile);
			
			// update local profile data
			userProfile.username = editedProfile.username;
			userProfile.first_name = editedProfile.first_name;
			userProfile.last_name = editedProfile.last_name;
			userProfile.email = editedProfile.email;
			
			successMessage = 'Profile updated successfully!';
			isEditingProfile = false;
		} catch (error) {
			console.error('Failed to update profile:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to update profile';
		} finally {
			isUpdatingProfile = false;
		}
	}

	function startEditingProfile() {
		editedProfile = {
			username: userProfile.username,
			first_name: userProfile.first_name,
			last_name: userProfile.last_name,
			email: userProfile.email
		};
		isEditingProfile = true;
	}

	function cancelEditingProfile() {
		isEditingProfile = false;
		errorMessage = null;
	}

	async function handleAddSocial(event: Event) {
		event.preventDefault();
		
		if (!selectedSocialType || !socialUsername) {
			errorMessage = 'Please select a social media type and enter a username';
			return;
		}
		
		try {
			isUpdatingSocial = true;
			errorMessage = null;
			successMessage = null;

			await updateSocialMedia(selectedSocialType, socialUsername);
			
			// refresh profile data
			userProfile = await fetchUserProfile();
			
			successMessage = 'Social media added successfully!';
			isAddingSocial = false;
			selectedSocialType = '';
			socialUsername = '';
		} catch (error) {
			console.error('Failed to add social media:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to add social media';
		} finally {
			isUpdatingSocial = false;
		}
	}

	async function handleRemoveSocial(socialType: string) {
		try {
			isUpdatingSocial = true;
			errorMessage = null;
			successMessage = null;

			await removeSocialMedia(socialType);
			
			// refresh profile data
			userProfile = await fetchUserProfile();
			
			successMessage = 'Social media removed successfully!';
		} catch (error) {
			console.error('Failed to remove social media:', error);
			errorMessage = error instanceof Error ? error.message : 'Failed to remove social media';
		} finally {
			isUpdatingSocial = false;
		}
	}

	function startEditingAbout() {
		editedAbout = userProfile?.about || '';
		isEditingAbout = true;
		aboutError = '';
	}

	function cancelEditingAbout() {
		isEditingAbout = false;
		editedAbout = '';
		aboutError = '';
	}

	async function handleAboutUpdate() {
		if (!editedAbout.trim()) {
			aboutError = 'About section cannot be empty';
			return;
		}
		
		isUpdatingAbout = true;
		aboutError = '';
		
		try {
			const result = await updateAbout(editedAbout);
			userProfile = { ...userProfile, about: result.about };
			isEditingAbout = false;
			successMessage = 'About section updated successfully';
		} catch (error) {
			aboutError = error instanceof Error ? error.message : 'Failed to update about section';
		} finally {
			isUpdatingAbout = false;
		}
	}

	function startEditingInterests() {
		editedInterests = [...(userProfile?.interests || [])];
		isEditingInterests = true;
		interestsError = '';
	}

	function cancelEditingInterests() {
		isEditingInterests = false;
		editedInterests = [];
		newInterest = '';
		interestsError = '';
	}

	function addInterest() {
		if (newInterest.trim()) {
			editedInterests = [...editedInterests, newInterest.trim()];
			newInterest = '';
		}
	}

	function removeInterest(index: number) {
		editedInterests = editedInterests.filter((_, i) => i !== index);
	}

	async function handleInterestsUpdate() {
		if (editedInterests.length === 0) {
			interestsError = 'Please add at least one interest';
			return;
		}
		
		isUpdatingInterests = true;
		interestsError = '';
		
		try {
			const result = await updateInterests(editedInterests);
			userProfile = { ...userProfile, interests: result.interests };
			isEditingInterests = false;
			successMessage = 'Interests updated successfully';
		} catch (error) {
			interestsError = error instanceof Error ? error.message : 'Failed to update interests';
		} finally {
			isUpdatingInterests = false;
		}
	}

	onMount(async () => {
		try {
			errorMessage = null;
			userProfile = await fetchUserProfile();
		} catch (error) {
			console.error('Failed to fetch user profile:', error);
			errorMessage = 'Failed to load profile. Please try again later.';
		}
	});
</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
	{#if errorMessage}
		<div class="alert alert-error mb-4 w-full max-w-2xl">
			<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span>{errorMessage}</span>
		</div>
	{/if}

	{#if successMessage}
		<div class="alert alert-success mb-4 w-full max-w-2xl">
			<svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
			</svg>
			<span>{successMessage}</span>
		</div>
	{/if}

	<div
		class="gap-13 flex grid w-full max-w-full grid-cols-1 flex-col justify-center md:grid-cols-2"
	>
		<!-- Left Column -->
		<div class="space-y-10">
			<div class="card bg-base-100 min-h-1/2 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<button class="hover:text-primary ml-auto" on:click={isEditingProfile ? cancelEditingProfile : startEditingProfile}>
							{@html pencil}
						</button>
					</div>
					<!-- Profile Image Container -->
					<div class="flex flex-col items-center">
						<div class="w-50 h-50 mb-4 overflow-hidden rounded-full">
							<!-- Profile Image or Placeholder -->
							{#if userProfile.profile_picture}
								<img
									src={userProfile.profile_picture}
									alt="Profile Picture"
									class="h-full w-full object-cover"
								/>
							{:else}
								<svg
									xmlns="http://www.w3.org/2000/svg"
									fill="none"
									viewBox="0 0 24 24"
									stroke-width="1.5"
									stroke="currentColor"
									class="h-full w-full object-cover"
								>
									<path
										stroke-linecap="round"
										stroke-linejoin="round"
										d="M17.982 18.725A7.488 7.488 0 0 0 12 15.75a7.488 7.488 0 0 0-5.982 2.975m11.963 0a9 9 0 1 0-11.963 0m11.963 0A8.966 8.966 0 0 1 12 21a8.966 8.966 0 0 1-5.982-2.275M15 9.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
									/>
								</svg>
							{/if}
						</div>
						<div class="flex flex-col items-center gap-2">
							<label class="btn btn-primary btn-sm">
								{#if isUploading}
									<span class="loading loading-spinner loading-xs"></span>
									Uploading...
								{:else}
									Change Picture
								{/if}
								<input
									type="file"
									accept="image/*"
									class="hidden"
									on:change={handleProfilePictureUpload}
									disabled={isUploading}
								/>
							</label>
						</div>
						<!-- Profile Information Section -->
						<div class="mb-4 w-full">
							<div class="mb-2 flex">
								<label for="user_name" class="label text-primary">
									<p class="label-text">Username:</p>
								</label>
								{#if isEditingProfile}
									<div class="flex flex-col ml-2">
										<input
											type="text"
											id="username"
											bind:value={editedProfile.username}
											class="input input-bordered input-sm {validationErrors.username ? 'input-error' : ''}"
											required
										/>
										{#if validationErrors.username}
											<p class="text-error text-xs mt-1">{validationErrors.username}</p>
										{/if}
									</div>
								{:else}
								<p class="text-user-info">{userProfile.username}</p>
								{/if}
							</div>
							<div class="mb-2 flex">
								<label for="name" class="label text-primary">
									<p class="label-text">Name:</p>
								</label>
								{#if isEditingProfile}
									<div class="flex flex-col ml-2">
										<div class="flex gap-2">
											<div class="flex flex-col">
												<input
													type="text"
													id="first_name"
													bind:value={editedProfile.first_name}
													class="input input-bordered input-sm {validationErrors.first_name ? 'input-error' : ''}"
													required
												/>
												{#if validationErrors.first_name}
													<p class="text-error text-xs mt-1">{validationErrors.first_name}</p>
												{/if}
											</div>
											<div class="flex flex-col">
												<input
													type="text"
													id="last_name"
													bind:value={editedProfile.last_name}
													class="input input-bordered input-sm {validationErrors.last_name ? 'input-error' : ''}"
													required
												/>
												{#if validationErrors.last_name}
													<p class="text-error text-xs mt-1">{validationErrors.last_name}</p>
												{/if}
											</div>
										</div>
									</div>
								{:else}
								<p class="text-user-info">{userProfile.first_name} {userProfile.last_name}</p>
								{/if}
							</div>
							<div class="mb-2 flex">
								<label for="email" class="label text-primary">
									<p class="label-text">Email:</p>
								</label>
								{#if isEditingProfile}
									<div class="flex flex-col ml-2">
										<input
											type="email"
											id="email"
											bind:value={editedProfile.email}
											class="input input-bordered input-sm {validationErrors.email ? 'input-error' : ''}"
											required
										/>
										{#if validationErrors.email}
											<p class="text-error text-xs mt-1">{validationErrors.email}</p>
										{/if}
									</div>
								{:else}
								<p class="text-user-info">{userProfile.email}</p>
								{/if}
							</div>
							{#if isEditingProfile}
								<div class="flex justify-end gap-2 mt-4">
									<button
										class="btn btn-sm btn-ghost"
										on:click={cancelEditingProfile}
										disabled={isUpdatingProfile}
									>
										Cancel
									</button>
									<button
										class="btn btn-sm btn-primary"
										on:click={handleProfileUpdate}
										disabled={isUpdatingProfile || Object.values(validationErrors).some(error => error)}
									>
										{#if isUpdatingProfile}
											<span class="loading loading-spinner loading-xs"></span>
											Updating...
										{:else}
											Save Changes
										{/if}
									</button>
								</div>
							{/if}
						</div>
					</div>
				</div>
			</div>
			<!-- Change Password Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<h1 class="text-primary mb-6 text-center text-4xl font-bold">Change Password</h1>
					<form class="space-y-4" on:submit={handlePasswordChange}>
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
													d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
												/>
											</svg>
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
													d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
												/>
											</svg>
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
													d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z"
												/>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"
												/>
											</svg>
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
						<div class="form-control mb-4 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-1/5"
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
			<!-- Socials Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">Socials</h1>
						</div>
						<button class="hover:text-primary" on:click={() => isAddingSocial = true}>
							{@html pencil}
						</button>
					</div>
					<div class="flex flex-wrap justify-center space-y-2">
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
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="size-6"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
												/>
											</svg>
										</button>
									</div>
								{/if}
							{/each}
						{/each}
					</div>

					{#if isAddingSocial}
						<form class="mt-4 space-y-4" on:submit={handleAddSocial}>
							<div class="form-control">
								<label class="label">
									<span class="label-text">Select Social Media</span>
								</label>
								<select 
									class="select select-bordered w-full"
									bind:value={selectedSocialType}
									required
								>
									<option value="">Choose a platform</option>
									{#each socialMedias as social}
										{#if !userProfile.social_type.includes(social.name)}
											<option value={social.name}>{social.name.charAt(0).toUpperCase() + social.name.slice(1)}</option>
										{/if}
									{/each}
								</select>
							</div>
							<div class="form-control">
								<label class="label">
									<span class="label-text">Username</span>
								</label>
								<input
									type="text"
									class="input input-bordered"
									bind:value={socialUsername}
									required
									placeholder="Enter your username"
								/>
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
									class="btn btn-primary"
									disabled={isUpdatingSocial}
								>
									{#if isUpdatingSocial}
										<span class="loading loading-spinner loading-xs"></span>
										Adding...
									{:else}
										Add Social Media
									{/if}
								</button>
							</div>
						</form>
					{/if}
				</div>
			</div>
			<!-- About Section -->
			<div class="card bg-base-100 shadow-4xl min-h-1/3 w-full rounded-3xl">
				<div class="card-body bg-secondary rounded-3xl">
					<div class="mb-4 flex items-center justify-between">
						<div class="flex-grow text-center">
							<h1 class="text-primary text-4xl font-bold">About</h1>
						</div>
						<button class="hover:text-primary" on:click={isEditingAbout ? cancelEditingAbout : startEditingAbout}>
							{@html pencil}
						</button>
					</div>
					{#if isEditingAbout}
						<div class="space-y-4">
							<textarea
								bind:value={editedAbout}
								rows="4"
								class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 {aboutError ? 'border-red-500' : ''}"
								placeholder="Tell us about yourself..."
							></textarea>
							{#if aboutError}
								<p class="text-red-500 text-sm">{aboutError}</p>
							{/if}
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
									class="btn btn-primary"
									disabled={isUpdatingAbout}
								>
									{#if isUpdatingAbout}
										<span class="loading loading-spinner loading-xs"></span>
										Updating...
									{:else}
										Save Changes
									{/if}
								</button>
							</div>
						</div>
					{:else}
						<p class="text-user-details whitespace-pre-wrap">{userProfile?.about || 'No bio available.'}</p>
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
						<button class="hover:text-primary" on:click={isEditingInterests ? cancelEditingInterests : startEditingInterests}>
							{@html pencil}
						</button>
					</div>
					{#if isEditingInterests}
						<div class="space-y-4">
							<div class="flex gap-2">
								<input
									type="text"
									bind:value={newInterest}
									class="input input-bordered flex-grow"
									placeholder="Add a new interest..."
									on:keydown={(e) => e.key === 'Enter' && addInterest()}
								/>
								<button
									class="btn btn-primary"
									on:click={addInterest}
								>
									Add
								</button>
							</div>
							<div class="flex flex-wrap gap-2">
								{#each editedInterests as interest, index}
									<div class="badge badge-primary gap-2">
										{interest}
										<button
											class="hover:text-error"
											on:click={() => removeInterest(index)}
										>
											×
								</button>
							</div>
						{/each}
							</div>
							{#if interestsError}
								<p class="text-error text-sm">{interestsError}</p>
							{/if}
							<div class="flex justify-end space-x-3">
								<button
									on:click={cancelEditingInterests}
									class="btn btn-ghost"
									disabled={isUpdatingInterests}
								>
									Cancel
								</button>
								<button
									on:click={handleInterestsUpdate}
									class="btn btn-primary"
									disabled={isUpdatingInterests}
								>
									{#if isUpdatingInterests}
										<span class="loading loading-spinner loading-xs"></span>
										Updating...
									{:else}
										Save Changes
									{/if}
						</button>
					</div>
						</div>
					{:else}
						<div class="flex flex-wrap gap-2">
							{#each userProfile?.interests || [] as interest}
								<div class="badge badge-primary">{interest}</div>
							{/each}
							{#if !userProfile?.interests?.length}
								<p class="text-user-details">No interests added yet.</p>
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</main>
