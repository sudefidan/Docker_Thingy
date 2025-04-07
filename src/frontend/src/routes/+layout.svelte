<script lang="ts">
	import '../app.css';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	let { children } = $props();

	async function logout() {
		const refreshToken = localStorage.getItem('refresh_token');

		if (refreshToken) {
			try {
				const response = await fetch('/api/logout/', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ refresh: refreshToken })
				});

				if (!response.ok) {
					console.error('Logout failed:', await response.json());
				}
			} catch (error) {
				console.error('Logout failed:', error);
			}
		}

		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');

		goto('http://localhost:5173/'); // Redirect to login page
	}
</script>

<main class="main-container">
	<!-- If it is not register or login page show: -->
	{#if page.url.pathname != '/register' && page.url.pathname != '/'}
		<!-- Left panel -->
		<div class="left-panel bg-secondary">
			<!-- Panel content -->
			<ul class="text-base-100 text-2xl">
				<li class="panel-item">
					<a href="/home" class="flex flex-row items-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill={page.url.pathname === '/home' ? 'var(--color-primary)' : 'currentColor'}
							class="size-8"
						>
							<path
								d="M11.47 3.841a.75.75 0 0 1 1.06 0l8.69 8.69a.75.75 0 1 0 1.06-1.061l-8.689-8.69a2.25 2.25 0 0 0-3.182 0l-8.69 8.69a.75.75 0 1 0 1.061 1.06l8.69-8.689Z"
							/>
							<path
								d="m12 5.432 8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 0 1-.75-.75v-4.5a.75.75 0 0 0-.75-.75h-3a.75.75 0 0 0-.75.75V21a.75.75 0 0 1-.75.75H5.625a1.875 1.875 0 0 1-1.875-1.875v-6.198a2.29 2.29 0 0 0 .091-.086L12 5.432Z"
							/>
						</svg>
						<span
							class="ml-2"
							style="color: {page.url.pathname === '/home'
								? 'var(--color-primary)'
								: 'currentColor'}">Hub</span
						>
					</a>
				</li>
				<li class="panel-item">
					<a href="/communities" class="flex flex-row items-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill={page.url.pathname === '/communities' ? 'var(--color-primary)' : 'currentColor'}
							class="size-8"
						>
							<path
								d="M8.25 6.75a3.75 3.75 0 1 1 7.5 0 3.75 3.75 0 0 1-7.5 0ZM15.75 9.75a3 3 0 1 1 6 0 3 3 0 0 1-6 0ZM2.25 9.75a3 3 0 1 1 6 0 3 3 0 0 1-6 0ZM6.31 15.117A6.745 6.745 0 0 1 12 12a6.745 6.745 0 0 1 6.709 7.498.75.75 0 0 1-.372.568A12.696 12.696 0 0 1 12 21.75c-2.305 0-4.47-.612-6.337-1.684a.75.75 0 0 1-.372-.568 6.787 6.787 0 0 1 1.019-4.38Z"
							/>
							<path
								d="M5.082 14.254a8.287 8.287 0 0 0-1.308 5.135 9.687 9.687 0 0 1-1.764-.44l-.115-.04a.563.563 0 0 1-.373-.487l-.01-.121a3.75 3.75 0 0 1 3.57-4.047ZM20.226 19.389a8.287 8.287 0 0 0-1.308-5.135 3.75 3.75 0 0 1 3.57 4.047l-.01.121a.563.563 0 0 1-.373.486l-.115.04c-.567.2-1.156.349-1.764.441Z"
							/>
						</svg>
						<span
							class="ml-2"
							style="color: {page.url.pathname === '/communities'
								? 'var(--color-primary)'
								: 'currentColor'}">Communities</span
						>
					</a>
				</li>
				<li class="panel-item">
					<a href="/events" class="flex flex-row items-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill={page.url.pathname === '/events' ? 'var(--color-primary)' : 'currentColor'}
							class="size-8"
						>
							<path
								d="M12.75 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM7.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM8.25 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM9.75 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM10.5 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12.75 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM14.25 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 17.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 13.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z"
							/>
							<path
								fill-rule="evenodd"
								d="M6.75 2.25A.75.75 0 0 1 7.5 3v1.5h9V3A.75.75 0 0 1 18 3v1.5h.75a3 3 0 0 1 3 3v11.25a3 3 0 0 1-3 3H5.25a3 3 0 0 1-3-3V7.5a3 3 0 0 1 3-3H6V3a.75.75 0 0 1 .75-.75Zm13.5 9a1.5 1.5 0 0 0-1.5-1.5H5.25a1.5 1.5 0 0 0-1.5 1.5v7.5a1.5 1.5 0 0 0 1.5 1.5h13.5a1.5 1.5 0 0 0 1.5-1.5v-7.5Z"
								clip-rule="evenodd"
							/>
						</svg>
						<span
							class="ml-2"
							style="color: {page.url.pathname === '/events'
								? 'var(--color-primary)'
								: 'currentColor'}">Events</span
						>
					</a>
				</li>
				<li class="panel-item">
					<a href="/notifications" class="flex flex-row items-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill={page.url.pathname === '/notifications'
								? 'var(--color-primary)'
								: 'currentColor'}
							class="size-8"
						>
							<path
								d="M5.85 3.5a.75.75 0 0 0-1.117-1 9.719 9.719 0 0 0-2.348 4.876.75.75 0 0 0 1.479.248A8.219 8.219 0 0 1 5.85 3.5ZM19.267 2.5a.75.75 0 1 0-1.118 1 8.22 8.22 0 0 1 1.987 4.124.75.75 0 0 0 1.48-.248A9.72 9.72 0 0 0 19.266 2.5Z"
							/>
							<path
								fill-rule="evenodd"
								d="M12 2.25A6.75 6.75 0 0 0 5.25 9v.75a8.217 8.217 0 0 1-2.119 5.52.75.75 0 0 0 .298 1.206c1.544.57 3.16.99 4.831 1.243a3.75 3.75 0 1 0 7.48 0 24.583 24.583 0 0 0 4.83-1.244.75.75 0 0 0 .298-1.205 8.217 8.217 0 0 1-2.118-5.52V9A6.75 6.75 0 0 0 12 2.25ZM9.75 18c0-.034 0-.067.002-.1a25.05 25.05 0 0 0 4.496 0l.002.1a2.25 2.25 0 1 1-4.5 0Z"
								clip-rule="evenodd"
							/>
						</svg>
						<span
							class="ml-2"
							style="color: {page.url.pathname === '/notifications'
								? 'var(--color-primary)'
								: 'currentColor'}">Notifications</span
						>
					</a>
				</li>
				<li class="panel-item">
					<a href={`/profile`} class="flex flex-row items-center">
						<svg
							xmlns="http://www.w3.org/2000/svg"
							viewBox="0 0 24 24"
							fill={page.url.pathname === `/profile` ? 'var(--color-primary)' : 'currentColor'}
							class="size-8"
						>
							<path
								fill-rule="evenodd"
								d="M18.685 19.097A9.723 9.723 0 0 0 21.75 12c0-5.385-4.365-9.75-9.75-9.75S2.25 6.615 2.25 12a9.723 9.723 0 0 0 3.065 7.097A9.716 9.716 0 0 0 12 21.75a9.716 9.716 0 0 0 6.685-2.653Zm-12.54-1.285A7.486 7.486 0 0 1 12 15a7.486 7.486 0 0 1 5.855 2.812A8.224 8.224 0 0 1 12 20.25a8.224 8.224 0 0 1-5.855-2.438ZM15.75 9a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z"
								clip-rule="evenodd"
							/>
						</svg>
						<span
							class="ml-2"
							style="color: {page.url.pathname === `/profile`
								? 'var(--color-primary)'
								: 'currentColor'}">Profile</span
						>
					</a>
				</li>
				<li class="panel-item">
					<hr class="border-base-100" />
				</li>
				<li class="panel-item">
					<button onclick={logout} class="flex flex-row items-center hover:text-primary">
						<svg class="size-8 panel-item-svg" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path
								d="M15 16.5V19C15 20.1046 14.1046 21 13 21H6C4.89543 21 4 20.1046 4 19V5C4 3.89543 4.89543 3 6 3H13C14.1046 3 15 3.89543 15 5V8.0625M11 12H21M21 12L18.5 9.5M21 12L18.5 14.5"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
						<span class="ml-2">Sign Out</span>
					</button>
				</li>
			</ul>
		</div>
		<!-- Main content -->
		<div class="main-content">
			{@render children()}
		</div>
	{:else}
		<!-- If it is register or login page show: -->
		<!-- Main content -->
		<div class="main-content">
			{@render children()}
		</div>
	{/if}
</main>
