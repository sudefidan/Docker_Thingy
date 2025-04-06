<script>
	import { goto } from '$app/navigation';
	import ShowPasswordIcon from '../assets/ShowPasswordIcon.svelte';
	let username = '';
	let password = '';
	let message = '';
	let showPassword = false;

	async function login() {
		try {
			const res = await fetch('http://127.0.0.1:8000/api/login/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (res.ok) {
				const data = await res.json();
				console.log(data);

				// Assuming the response contains the access token in data.access
				if (data.access) {
					// Store the access token in localStorage
					localStorage.setItem('access_token', data.access);

					// After successful login, forward to homepage
					goto('/home'); // Redirect to the home page or another protected route
					if (data.refresh) {
						localStorage.setItem('refresh_token', data.refresh);
					}
				} else {
					message = 'Failed to login! No access token received.';
				}
			} else {
				const data = await res.json();
				message = 'Invalid username or password!';
				// Clear the form inputs
				username = '';
				password = '';
			}
		} catch (error) {
			console.error(error);
			message = 'An error occurred. Please try again!';
		}
	}
</script>

<main class="flex items-center justify-center">
	<div class="card bg-base-100 shadow-4xl max-7xl w-full rounded-3xl">
		<div class="card-body bg-secondary rounded-3xl p-10">
			<h1 class="text-primary mb-6 mt-2 text-center text-4xl font-bold">Login to UniHub</h1>
			<form on:submit|preventDefault={login}>
				<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="username" class="label">
							<span class="label-text">Username</span>
						</label>
						<input
							type="text"
							bind:value={username}
							name="username"
							class="input input-bordered validator custom-input"
							required
							pattern="[A-Za-z][A-Za-z0-9\-_]*"
							minlength="3"
							maxlength="30"
							title="Must contain only letters, numbers or dash,or underscores!"
							autocomplete="email"
							placeholder="Enter your username"
						/>
					</div>
				</div>
				<div class="form-control mb-2 flex flex-col gap-3 pt-6 sm:flex-row">
					<div class="w-full">
						<label for="password" class="label">
							<span class="label-text">Password</span>
						</label>
						<div class="relative">
							<input
								type={showPassword ? 'text' : 'password'}
								name="password"
								bind:value={password}
								class="input input-bordered validator custom-input pr-9"
								required
								minlength="8"
								autocomplete="current-password"
								placeholder="Enter your password"
							/>
							<button
								type="button"
								class="absolute inset-y-0 right-0 flex items-center pr-3 text-sm leading-5"
								on:click={() => (showPassword = !showPassword)}
							>
								{#if showPassword}
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
				</div>
				<div class="form-control text-primary flex justify-center pt-2 text-center">
					{#if message}
						<p>{message}</p>
					{:else}
						<p class="invisible flex">PlaceholderPlaceholderPlaceholder</p>
					{/if}
				</div>
				<div class="form-control mb-4 flex justify-center pt-4">
					<button class="btn btn-primary text-secondary hover:bg-primary-focus w-1/5" type="submit"
						>Login</button
					>
				</div>
				<p class="text-base-100 mt-2 text-center text-sm/6">
					Not a member?
					<a href="/register" class="text-primary hover:text-base-100 font-semibold">Register</a>
				</p>
			</form>
		</div>
	</div>
</main>
