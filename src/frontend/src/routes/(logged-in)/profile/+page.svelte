<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import { CATEGORIES } from '../../../assets/categories.json';
	import AddIcon from '../../../assets/AddIcon.svelte';
	import EditIcon from '../../../assets/EditIcon.svelte';
	import ShowPasswordIcon from '../../../assets/ShowPasswordIcon.svelte';
	import SettingsIcon from '../../../assets/SettingsIcon.svelte';

	import {
		fetchUserProfile,
		type UserProfile,
		updateProfilePicture,
		updateProfile,
		updateSocialMedia,
		removeSocialMedia,
		socialMedias,
		updateAbout,
		addInterest,
		removeInterest
	} from '$lib/api/profile';
	import { changePassword } from '$lib/api/password';
	import RemoveIcon from '../../../assets/RemoveIcon.svelte';
	import MediaIcon from '../../../assets/MediaIcon.svelte';

	let categories = [...CATEGORIES.sort((a, b) => a.trim().localeCompare(b.trim())), 'Other']; // Sort the categories alphabetically

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
		interests: [],
		address: '',
		program: '',
		uni_year: ''
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
		email: '',
		address: '',
		program: '',
		uni_year: ''
	};

	// Settings menu state
	let showSettingsMenu = false;
	let showDeleteConfirmation = false;
	let showPasswordChangeModal = false;

	let tempProfilePicture = ''; // Temporary variable for profile picture upload

	// Social media section editing
	let isAddingSocial = false;
	let selectedSocialType = '';
	let socialUsername = '';
	let isUpdatingSocial = false;

	// About editing
	let isEditingAbout = false;
	let editedAbout = '';
	let isUpdatingAbout = false;

	// Interests section editing
	let isEditingInterests = false;
	let isUpdatingInterests = false;
	let newInterest = '';
	let editedInterests: string[] = []; // Define editedInterests as an array

	// Notification modal state
	let showNotificationModal = false;
	let notificationMessage = '';

	let clickOutsideHandler: any; // Variable to store the click event handler

	let followerCount = 0; // Initialise follower count
	let followingCount = 0; // Initialise following count
	let isFollowersModalOpen = false; // Initialise followers modal state
	let isFollowingModalOpen = false; // Initialise following modal state
	let followers = []; // Initialise followers list
	let following = []; // Initialise following list
	let loadingFollowers = false; // Initialise loading state for followers
	let loadingFollowing = false; // Initialise loading state for following

	// Function to handle adding an interest
    async function handleAddInterest(event) {
        event.preventDefault();

        if (!newInterest) {
            return;
        }

        try {
            isUpdatingInterests = true;
            userProfile = await addInterest(newInterest);
            newInterest = '';
            isEditingInterests = false;
        } catch (error) {
            console.error('Failed to add interest:', error);
            let errorMessage = error instanceof Error ? error.message : 'Failed to add interest';
            alert(errorMessage + '. Please try again!');
        } finally {
            isUpdatingInterests = false;
        }
    }

	// Function to handle removing an interest
    async function handleRemoveInterest(interest) {
        try {
            isUpdatingInterests = true;
            userProfile = await removeInterest(interest);
        } catch (error) {
            console.error('Failed to remove interest:', error);
            let errorMessage = error instanceof Error ? error.message : 'Failed to remove interest';
            alert(errorMessage + '. Please try again!');
        } finally {
            isUpdatingInterests = false;
        }
    }

	// Function to show followers modal
	async function showFollowersModal() {
		isFollowersModalOpen = true;
		await fetchFollowers();
	}

	// Function to show following modal
	async function showFollowingModal() {
		isFollowingModalOpen = true;
		await fetchFollowing();
	}

	// Function to fetch followers
	async function fetchFollowers() {
		try {
			loadingFollowers = true;
			const token = localStorage.getItem('access_token');

			const response = await fetch('http://127.0.0.1:8000/api/connections/followers/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (response.ok) {
				const data = await response.json();
				followers = data.followers;
			} else {
				console.error('Failed to fetch followers');
			}
		} catch (error) {
			console.error('Error fetching followers:', error);
		} finally {
			loadingFollowers = false;
		}
	}

	// Function to fetch following
	async function fetchFollowing() {
		try {
			loadingFollowing = true;
			const token = localStorage.getItem('access_token');

			const response = await fetch('http://127.0.0.1:8000/api/connections/following/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (response.ok) {
				const data = await response.json();
				following = data.following;
			} else {
				console.error('Failed to fetch following');
			}
		} catch (error) {
			console.error('Error fetching following:', error);
		} finally {
			loadingFollowing = false;
		}
	}

	// Function to toggle follow/unfollow
	async function toggleFollow(userId, isFollowing) {
		try {
			const token = localStorage.getItem('access_token');
			const endpoint = isFollowing ? 'unfollow' : 'follow';

			const response = await fetch(`http://127.0.0.1:8000/api/${endpoint}/${userId}/`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (response.ok) {
				// Update followers/following lists
				if (isFollowersModalOpen) await fetchFollowers();
				if (isFollowingModalOpen) await fetchFollowing();

				// Update connection counts
				await fetchConnectionCounts();
			} else {
				console.error(`Failed to ${isFollowing ? 'unfollow' : 'follow'} user`);
			}
		} catch (error) {
			console.error('Error toggling follow status:', error);
		}
	}

	// Function to close follwers modal
	function closeFollowersModal() {
		isFollowersModalOpen = false;
	}

	// Function to close following modal
	function closeFollowingModal() {
		isFollowingModalOpen = false;
	}

	// Fetch connection counts
	async function fetchConnectionCounts() {
		try {
			const token = localStorage.getItem('access_token');
			if (!token) return;

			const response = await fetch('http://127.0.0.1:8000/api/connections/counts/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (response.ok) {
				const data = await response.json();
				followerCount = data.follower_count;
				followingCount = data.following_count;
			} else {
				console.error('Failed to fetch connection counts');
			}
		} catch (error) {
			console.error('Error fetching connection counts:', error);
		}
	}

	// Function to handle click outside the settings menu
	function handleClickOutside(event: MouseEvent) {
		const settingsMenuElement = document.getElementById('settings-menu');
		const settingsButtonElement = document.getElementById('settings-button');

		if (
			settingsMenuElement &&
			!settingsMenuElement.contains(event.target as Node) &&
			!settingsButtonElement?.contains(event.target as Node)
		) {
			showSettingsMenu = false;
		}
	}

	// Function to toggle settings menu
	function toggleSettingsMenu() {
		showSettingsMenu = !showSettingsMenu;
	}

	// Function to show notification
	function showNotification(message: string) {
		notificationMessage = message;
		showNotificationModal = true;

		// Automatically hide the notification after 5 seconds
		setTimeout(() => {
			showNotificationModal = false;
		}, 5000);
	}

	// Function to close the notification
	function closeNotification() {
		showNotificationModal = false;
	}

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

			// Check if email was changed
			const emailChanged = userProfile.email !== editedProfile.email;

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
			userProfile.address = editedProfile.address;
			userProfile.program = editedProfile.program;
			userProfile.uni_year = editedProfile.uni_year;
			isEditingProfile = false;

			// Show notification if email was changed
			if (emailChanged) {
				showNotification(
					'A verification email has been sent to your new email address. Please verify your email to complete the change.'
				);
			}
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
			email: userProfile.email,
			address: userProfile.address,
			program: userProfile.program,
			uni_year: userProfile.uni_year
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

	onMount(async () => {
		try {
			// Fetch initial data on the client-side
			userProfile = await fetchUserProfile();
			await fetchConnectionCounts();
		} catch (error) {
			console.error('Failed to fetch user profile or connection counts:', error);
		}

		// Add event listener for click outside the settings menu, only in browser
		if (browser) {
			clickOutsideHandler = (event: MouseEvent) => handleClickOutside(event);
			document.addEventListener('click', clickOutsideHandler);
		}
	});

	// Add event listener for click outside the settings menu
	onMount(() => {
		clickOutsideHandler = (event: MouseEvent) => handleClickOutside(event);
		if (browser) {
			document.addEventListener('click', clickOutsideHandler);
		}
	});

	// Cleanup event listener on component destroy
	onDestroy(() => {
		if (browser) {
			document.removeEventListener('click', clickOutsideHandler);
		}
	});

	// Function to handle delete account action
	async function handleDeleteAccount() {
		const confirmed = confirm(
			'Are you sure you want to delete your account? This action cannot be undone.'
		);
		if (confirmed) {
			try {
				// Call your API to delete account
				const response = await fetch('http://127.0.0.1:8000/api/users/delete/', {
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${localStorage.getItem('access_token')}`
					}
				});

				if (response.ok) {
					// Clear local storage and redirect to login
					localStorage.removeItem('access_token');
					window.location.href = '/';
				} else {
					const data = await response.json();
					alert(data.error || 'Failed to delete account');
				}
			} catch (error) {
				console.error('Error deleting account:', error);
				alert('An error occurred while trying to delete your account');
			}
		}
	}

	// Function to toggle delete confirmation modal
	function togglePasswordChangeModal() {
		showPasswordChangeModal = !showPasswordChangeModal;
	}
</script>

<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-10">
	<!-- Main content area -->
	<div
		class="gap-13 flex grid w-full max-w-full grid-cols-1 flex-col justify-center md:grid-cols-2"
	>
		<!-- Floating Settings Button -->
		<button
			id="settings-button"
			class="fixed bottom-5 right-5 bg-primary text-secondary pl-3 pr-4 pt-4 pb-4 rounded-full shadow-lg hover:bg-primary-focus z-50"
			on:click|stopPropagation={toggleSettingsMenu}
		>
			<SettingsIcon size={30} />
		</button>

		<!-- Settings dropdown menu -->
		{#if showSettingsMenu}
			<div
				id="settings-menu"
				class="absolute right-0 bottom-16 w-56 bg-secondary rounded-lg shadow-xl z-50 border border-base-100"
				on:click|stopPropagation
			>
				<div class="p-2">
					<h3 class="text-primary font-bold text-lg px-3 py-2">Account Settings</h3>

					<!-- Show password change option -->
					<button
						class="w-full text-left px-3 py-2 hover:bg-base-200 rounded-md flex items-center"
						on:click={() => {
							toggleSettingsMenu();
							showPasswordChangeModal = true;
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 mr-2"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
							/>
						</svg>
						Change Password
					</button>

					<!-- Delete account option -->
					<button
						class="w-full text-left px-3 py-2 hover:bg-base-200 rounded-md flex items-center"
						on:click={() => {
							toggleSettingsMenu();
							handleDeleteAccount();
						}}
					>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5 mr-2"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
							/>
						</svg>
						Delete Account
					</button>
				</div>
			</div>
		{/if}

		<!-- Password Change Modal -->
		{#if showPasswordChangeModal}
			<div
				style="background-color: rgba(0, 0, 0, 0.8);"
				class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
				on:click={togglePasswordChangeModal}
			>
				<div
					class="card bg-secondary pl-5 pb-7 pr-7 pt-10 rounded-3xl w-full max-w-md"
					on:click|stopPropagation
				>
					<h1 class="text-primary mb-6 text-center text-3xl font-bold">Change Password</h1>

					<form class="space-y-4" on:submit|preventDefault={handlePasswordChange}>
						<div class="form-control">
							<label for="current_password" class="label">
								<span class="label-text">Current Password</span>
							</label>
							<div class="relative">
								<input
									type={showCurrentPassword ? 'text' : 'password'}
									name="current_password"
									bind:value={currentPassword}
									class="input input-bordered validator w-full custom-input pr-9"
									required
									minlength="8"
									autocomplete="current-password"
									placeholder="Enter your current password"
								/>
								<button
									type="button"
									class="absolute inset-y-0 right-0 flex items-center pr-3 text-sm leading-5"
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
							</div>
						</div>
						<div class="form-control">
							<label for="new_password" class="label">
								<span class="label-text">New Password</span>
							</label>
							<div class="relative">
								<input
									type={showNewPassword ? 'text' : 'password'}
									name="new_password"
									bind:value={newPassword}
									class="input input-bordered validator w-full custom-input pr-9"
									required
									minlength="8"
									autocomplete="new-password"
									placeholder="Enter your new password"
								/>
								<button
									type="button"
									class="absolute inset-y-0 right-0 flex items-center pr-3 text-sm leading-5"
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
							</div>
						</div>

						<div class="form-control">
							<label for="confirm_password" class="label">
								<span class="label-text">Confirm Password</span>
							</label>
							<div class="relative">
								<input
									type={showConfirmPassword ? 'text' : 'password'}
									name="confirm_password"
									bind:value={confirmPassword}
									class="input input-bordered validator w-full custom-input pr-9"
									required
									minlength="8"
									autocomplete="new-password"
									placeholder="Confirm your new password"
								/>
								<button
									type="button"
									class="absolute inset-y-0 right-0 flex items-center pr-3 text-sm leading-5"
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
							</div>
						</div>

						<div class="fform-control mb-2 mt-6 flex justify-center">
							<button
								class="btn btn-primary text-secondary hover:bg-primary-focus w-auto pl-10 pr-10"
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
		{/if}

		<!-- Left Column -->
		<div class="space-y-10">
			<!-- Profile Section -->
			<div class="card bg-base-100 min-h-[80vh] w-full rounded-3xl">
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
						<div class="relative w-70 h-70 mt-0 mb-10">
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
								<div class="absolute inset-0 flex items-center justify-center upload-button">
									<label class="flex items-center justify-center cursor-pointer" for="file-upload">
										<MediaIcon size={28} />
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
							<div class="flex justify-center items-center gap-16 mb-15">
								<div
									class="flex flex-col items-center cursor-pointer hover:text-primary"
									on:click={showFollowersModal}
								>
									<span class="text-2xl font-bold text-primary">{followerCount || 0}</span>
									<span class="text-sm">Followers</span>
								</div>
								<div
									class="flex flex-col items-center cursor-pointer hover:text-primary"
									on:click={showFollowingModal}
								>
									<span class="text-2xl font-bold text-primary">{followingCount || 0}</span>
									<span class="text-sm">Following</span>
								</div>
							</div>
							<div class="mb-5 flex justify-between items-center">
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
							<div class="mb-5 flex justify-between items-center">
								<label for="name" class="label text-primary">
									<p class="label-text">Name:</p>
								</label>
								{#if isEditingProfile}
									<div class="flex gap-2 m-0">
										<input
											type="text"
											id="first_name"
											bind:value={editedProfile.first_name}
											class="input input-bordered validator custom-input-profile"
											required
											pattern="[A-Za-z]+"
											minlength="1"
										/>
										<input
											type="text"
											id="last_name"
											bind:value={editedProfile.last_name}
											class="input input-bordered validator custom-input-profile"
											required
											pattern="[A-Za-z]+"
										/>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.first_name} {userProfile.last_name}</p>
								{/if}
							</div>
							<div class="mb-5 flex justify-between items-center">
								<label for="email" class="label text-primary">
									<p class="label-text">Email:</p>
								</label>
								{#if isEditingProfile}
									<div>
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
							<div class="mb-5 flex justify-between items-center">
								<label for="address" class="label text-primary">
									<p class="label-text">Address:</p>
								</label>
								{#if isEditingProfile}
									<div>
										<input
											type="text"
											id="address"
											bind:value={editedProfile.address}
											class="input input-bordered validator custom-input-profile"
										/>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.address}</p>
								{/if}
							</div>
							<div class="mb-5 flex justify-between items-center">
								<label for="program" class="label text-primary">
									<p class="label-text">Program:</p>
								</label>
								{#if isEditingProfile}
									<div>
										<input
											type="text"
											id="program"
											bind:value={editedProfile.program}
											class="input input-bordered validator custom-input-profile"
										/>
									</div>
								{:else}
									<p class="text-user-info">{userProfile.program}</p>
								{/if}
							</div>
							<div class="mb-5 flex justify-between items-center">
								<label for="year" class="label text-primary">
									<p class="label-text">Year:</p>
								</label>
								{#if isEditingProfile}
									<div>
										<select
											id="year"
											bind:value={editedProfile.uni_year}
											class="select select-bordered validator custom-input placeholder-selected"
										>
											<option value="">Select year</option>
											<option value={1} selected={userProfile.uni_year === '1'}>Year 1</option>
											<option value={2} selected={userProfile.uni_year === '2'}>Year 2</option>
											<option value={3} selected={userProfile.uni_year === '3'}>Year 3</option>
										</select>
									</div>
								{:else}
									<p class="text-user-info">
										{#if userProfile.uni_year === '1'}
											Year 1
										{:else if userProfile.uni_year === '2'}
											Year 2
										{:else if userProfile.uni_year === '3'}
											Year 3
										{:else}
											{userProfile.uni_year || ''}
										{/if}
									</p>
								{/if}
							</div>

							<div class="flex justify-end gap-2 mt-6 mb-0" class:invisible={!isEditingProfile}>
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
		</div>

		<!-- Right Column -->
		<div class="space-y-10">
			<!-- About Section -->
			<div class="card bg-base-100 shadow-4xl min-h-[25.7vh] w-full rounded-3xl">
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
						<div class="form-control flex flex-col gap-3 w-full">
							<textarea
								bind:value={editedAbout}
								rows="3"
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
			<div class="card bg-base-100 shadow-4xl min-h-[31.5vh] w-full rounded-3xl">
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
						<form class="form-control flex flex-col gap-3" on:submit={handleAddSocial}>
							<div class="w-full">
								<label class="label">
									<span class="label-text">Select Social Media</span>
								</label>
								<div class="relative flex items-center">
									<select
										class="select select-bordered custom-input flex-grow placeholder-selected"
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
			<div class="card bg-base-100 shadow-4xl min-h-[24.5vh] w-full rounded-3xl">
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
						<form class="form-control flex flex-col gap-3" on:submit={handleAddInterest}>
							<div class="w-full">
								<label class="label">
									<span class="label-text">Select an interest</span>
								</label>
								<div class="relative flex items-center">
									<select
										class="select select-bordered custom-input flex-grow placeholder-selected"
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
							{#each userProfile.interests as interest}
								<div class="border-base-100 m-1 flex space-x-2 rounded-lg border-2 p-2">
									<p class="text-user-details pr-2">{interest}</p>
									<button
										class="hover:text-primary"
										on:click={() => handleRemoveInterest(interest)}
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

	<!-- Notification Modal -->
	{#if showNotificationModal}
		<div class="fixed inset-x-0 top-0 mt-4 flex items-center justify-center z-50">
			<div class="bg-secondary rounded-lg p-4 shadow-lg max-w-md mx-auto">
				<div class="flex items-center">
					<!-- Email Icon -->
					<svg
						xmlns="http://www.w3.org/2000/svg"
						class="h-6 w-6 text-primary mr-2"
						fill="none"
						viewBox="0 0 24 24"
						stroke="currentColor"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
						/>
					</svg>

					<div class="flex-1">
						<p class="font-medium">{notificationMessage}</p>
					</div>

					<!-- Close Button -->
					<button class="ml-4 text-primary hover:text-base-100" on:click={closeNotification}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-5 w-5"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>
	{/if}
	<!-- Followers Modal -->
	{#if isFollowersModalOpen}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
			on:click={closeFollowersModal}
		>
			<div
				class="card bg-secondary rounded-3xl p-6 max-w-lg min-w-[40%] w-full max-h-[80vh] overflow-y-auto"
				on:click|stopPropagation
			>
				<!-- Modal Header -->
				<div class="flex justify-between items-center mb-4">
					<h2 class="text-2xl font-bold text-primary">Followers</h2>
					<button class="text-primary hover:text-base-100" on:click={closeFollowersModal}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<!-- Loading State -->
				{#if loadingFollowers}
					<div class="flex justify-center items-center py-8">
						<span class="loading loading-spinner loading-lg text-primary"></span>
					</div>
					<!-- Empty State -->
				{:else if followers.length === 0}
					<div class="text-center py-8">
						<p class="text-lg">You don't have any followers yet.</p>
					</div>
					<!-- Followers List -->
				{:else}
					<div class="space-y-4">
						{#each followers as follower}
							<div class="flex items-center justify-between p-3 border-b border-base-100">
								<!-- User Info -->
								<div class="flex items-center gap-3">
									<!-- Profile Picture -->
									{#if follower.profile_picture}
										<img
											src={`data:image/jpeg;base64,${follower.profile_picture}`}
											alt="Profile"
											class="w-12 h-12 rounded-full object-cover"
										/>
									{:else}
										<div
											class="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												viewBox="0 0 24 24"
												class="w-8 h-8 text-gray-500"
											>
												<path
													fill="currentColor"
													d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
												/>
											</svg>
										</div>
									{/if}

									<!-- User Name and Username -->
									<div>
										<p class="font-bold">{follower.first_name} {follower.last_name}</p>
										<p class="text-gray-500">@{follower.username}</p>
									</div>
								</div>

								<!-- Follow/Unfollow Button -->
								<button
									class="btn btn-sm {follower.is_following
										? 'btn-outline'
										: 'btn-primary text-secondary'}"
									on:click={() => toggleFollow(follower.id, follower.is_following)}
								>
									{follower.is_following ? 'Unfollow' : 'Follow'}
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}

	<!-- Following Modal -->
	{#if isFollowingModalOpen}
		<div
			style="background-color: rgba(0, 0, 0, 0.8);"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
			on:click={closeFollowingModal}
		>
			<div
				class="card bg-secondary rounded-3xl p-6 max-w-lg min-w-[40%] w-full max-h-[80vh] overflow-y-auto"
				on:click|stopPropagation
			>
				<!-- Modal Header -->
				<div class="flex justify-between items-center mb-4">
					<h2 class="text-2xl font-bold text-primary">Following</h2>
					<button class="text-primary hover:text-base-100" on:click={closeFollowingModal}>
						<svg
							xmlns="http://www.w3.org/2000/svg"
							class="h-6 w-6"
							fill="none"
							viewBox="0 0 24 24"
							stroke="currentColor"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M6 18L18 6M6 6l12 12"
							/>
						</svg>
					</button>
				</div>

				<!-- Loading State -->
				{#if loadingFollowing}
					<div class="flex justify-center items-center py-8">
						<span class="loading loading-spinner loading-lg text-primary"></span>
					</div>
					<!-- Empty State -->
				{:else if following.length === 0}
					<div class="text-center py-8">
						<p class="text-lg">You're not following anyone yet.</p>
					</div>
					<!-- Following List -->
				{:else}
					<div class="space-y-4">
						{#each following as user}
							<div class="flex items-center justify-between p-3 border-b border-base-100">
								<!-- User Info -->
								<div class="flex items-center gap-3">
									<!-- Profile Picture -->
									{#if user.profile_picture}
										<img
											src={`data:image/jpeg;base64,${user.profile_picture}`}
											alt="Profile"
											class="w-12 h-12 rounded-full object-cover"
										/>
									{:else}
										<div
											class="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center"
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												viewBox="0 0 24 24"
												class="w-8 h-8 text-gray-500"
											>
												<path
													fill="currentColor"
													d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"
												/>
											</svg>
										</div>
									{/if}

									<!-- User Name and Username -->
									<div>
										<p class="font-bold">{user.first_name} {user.last_name}</p>
										<p class="text-gray-500">@{user.username}</p>
									</div>
								</div>

								<!-- Unfollow Button -->
								<button class="btn btn-sm btn-outline" on:click={() => toggleFollow(user.id, true)}>
									Unfollow
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</main>
