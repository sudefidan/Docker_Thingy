<script lang="ts">
	import { onMount } from "svelte";
	import { page } from "$app/stores"; 

	/*let user_id = $page.params.user_id;

	async function loadProfile() {
		const profile = await fetchUserProfile(user_id);
		if (profile) {
			userProfile = profile;
		}
	}*/
	let userProfile = { profile_picture: "", username: "test123", first_name: "Johnny", last_name: "Sins", social_type: "X", social_username: "J_Sins24", about: "satisfying clients no matter the cost" };

</script>

<main class="flex items-center justify-center">
	<div class="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-5xl">
		<!-- Left Column (2 boxes) -->
		<div class="card bg-base-100 shadow-4xl w-full rounded-3xl">
			<div class="card-body bg-secondary rounded-3xl p-10">
				<div class="profile-container">
					<h2 class="text-lg font-bold mb-4">User Profile</h2>
					
					<!-- Profile Picture Section -->
					<div class="flex items-center mb-6">
						<!-- Profile Image Container -->
						<div class="w-20 h-20 rounded-full overflow-hidden mr-4">
							<!-- Profile Image or Placeholder -->
							<img src="{userProfile.profile_picture}" alt="Profile Picture" class="w-full h-full object-cover">
						</div>
						<div>
							<p><strong>Username:</strong> {userProfile.username}</p>
							<p><strong>Forename:</strong> {userProfile.first_name}</p>
							<p><strong>Surname:</strong> {userProfile.last_name}</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div class="card bg-base-100 shadow-4xl w-full rounded-3xl">
			<div class="card-body bg-secondary rounded-3xl p-10">
				<div class="profile-container">
					<h2 class="text-lg font-bold mb-4">Socials</h2>
					<div class="profile-section">
						<p><strong>Socials:</strong> {userProfile.social_type} {"-"} {userProfile.social_username} </p>
						<p><strong>About:</strong> {userProfile.about || "No bio available."}</p>
					</div>
				</div>
			</div>
		</div>

		<!-- Right Column (1 box) -->
		<div class="card bg-base-100 shadow-4xl w-full rounded-3xl col-span-1 md:col-span-2">
			<div class="card-body bg-secondary rounded-3xl p-6">
				<div class="profile-container">
					<h2 class="text-lg font-bold mb-2">Change Password</h2>
					<form class="space-y-1">
						<div>
							<label class="block text-sm font-medium mb-1">Current Password</label>
							<input type="password" class="input input-bordered w-full" placeholder="Enter current password" required>
						</div>
		
						<div>
							<label class="block text-sm font-medium mb-1">New Password</label>
							<input type="password" class="input input-bordered w-full" placeholder="Enter new password" required>
						</div>
		
						<div>
							<label class="block text-sm font-medium mb-1">Confirm New Password</label>
							<input type="password" class="input input-bordered w-full" placeholder="Confirm new password" required>
						</div>
		
						<button type="submit" class="btn btn-primary w-full">Update Password</button>
					</form>
				</div>
			</div>
		</div>
		
	</div>
</main>
