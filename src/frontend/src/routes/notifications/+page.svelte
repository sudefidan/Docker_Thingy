<script>
	let access_token = $state(null);
	let notifications = $state(null);

	$effect(() => {
		// Get the access token from localStorage
		access_token = localStorage.getItem('access_token');

		// If no token, redirect to login
		if (!access_token) {
			window.location.href = '/';
		} else {
			get_notifications();
		}
	});

	const get_notifications = async () => {
		try {
			const response = await fetch('http://127.0.0.1:8000/api/notifications/', {
				method: 'GET',
				headers: {
					Authorization: `Bearer ${access_token}`
				}
			});

			if (response.ok) {
				const data = await response.json();
				console.log('Fetched all notifications:', data);
				notifications = data; // This will trigger reactivity in Svelte
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};

	const dismiss = async (notification_id) => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/api/notifications/delete/${notification_id}/`,
				{
					method: 'DELETE',
					headers: {
						Authorization: `Bearer ${access_token}`
					}
				}
			);

			if (response.ok) {
				location.reload();
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};
</script>

{#if notifications && Array.isArray(notifications) && notifications.length > 0}
	<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5">
		<div class="gap-13 flex grid w-full w-full grid-cols-1 flex-col justify-center md:grid-cols-2">
			{#each notifications as notification}
				<div class="card bg-base-100 min-h-1/2 w-full rounded-3xl">
					<div class="card-body bg-secondary rounded-3xl">
						<h1 class="text-primary mb-1 text-center text-4xl font-bold">Notification</h1>
						<div class="card bg-base-100 min-h-1/2 w-full">
							<div class="card-body bg-secondary">
								<div class="w-full">
									<p class="text-xl">Message: {notification.message}</p>
									<p class="text-lg">
										Timestamp: {new Date(notification.timestamp).toLocaleString()}
									</p>
								</div>
							</div>
							<div class="card-actions bg-secondary justify-end">
								<button
									class="btn btn-primary"
									onclick={() => {
										dismiss(notification.notification_id);
									}}>Dismiss</button
								>
							</div>
						</div>
					</div>
				</div>
			{/each}
		</div>
	</main>
{:else}
	<p>No notifications to show...</p>
{/if}
