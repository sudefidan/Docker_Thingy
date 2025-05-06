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
				// Sort notifications by timestamp (newest first)
                notifications = data.sort((a, b) => {
                    return new Date(b.timestamp) - new Date(a.timestamp);
                });
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
				// Instead of reloading the page, just update the notifications list
                notifications = notifications.filter(n => n.notification_id !== notification_id);
			} else {
				console.error('Failed to fetch communities');
			}
		} catch (error) {
			console.error('Network error:', error.message);
		}
	};
</script>

{#if notifications && Array.isArray(notifications) && notifications.length > 0}
	<main class="pl-13 pr-13 mb-5 flex w-full flex-col items-center overflow-auto pt-5 mt-5">
		<div class="grid grid-cols-1 gap-4 w-full">
			{#each notifications as notification}
				<div class="card bg-base-100 mb-5 shadow-4xl w-full rounded-3xl">
					<div class="card-body bg-secondary rounded-3xl">
						<div class="w-full">
							 <p class="text-primary text-2xl">{notification.message}</p>
							 <p class="text-base-100 text-lg">
                                {new Date(notification.timestamp).toLocaleString()}
                            </p>
							<div class="card-actions bg-secondary justify-end">
								<button
									class="btn btn-primary text-secondary hover:bg-primary-focus w-auto"
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
