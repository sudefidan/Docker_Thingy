<script lang="ts">
	import { enhance } from '$app/forms';
	import { goto } from '$app/navigation';

	let showPassword = false;
	let registerForm: HTMLFormElement;

	interface CustomResult {
		message?: string;
		error?: string;
		access?: string;
		refresh?: string;
	}

</script>

<main class="flex items-center justify-center">
	<div class="card bg-base-100 shadow-4xl w-full max-w-3xl rounded-3xl">
		<div class="card-body bg-secondary rounded-3xl p-10">
			<h1 class="text-primary mb-6 mt-2 text-center text-4xl font-bold">Register with UniHub</h1>
			<form
				method="POST"
				action="http://127.0.0.1:8000/api/register/"
				bind:this={registerForm}
				use:enhance={() => {
					return async ({ update, result }) => {
						const customResult = result as CustomResult;
						if (customResult?.message) {
							// Save the tokens to local storage and push onto the main ;D
							if (customResult.access && customResult.refresh) {
								localStorage.setItem('access_token', customResult.access);
								localStorage.setItem('refresh_token', customResult.refresh);
							}
							// Redirect to the home page like a boss :D
							goto('/home');
							registerForm.reset();
						} else if (customResult?.error) {
							alert(customResult.error);
						}
						await update({ invalidateAll: true });
					};
				}}
				class="space-y-4"
			>
				<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="first_name" class="label">
							<span class="label-text">First Name</span>
						</label>
						<input
							type="text"
							name="first_name"
							class="input input-bordered validator custom-input"
							required
							autocomplete="given-name"
							pattern="[A-Za-z]+"
							placeholder="Enter your first name"
						/>
						<p class="validator-hint">Must be more than 1 character containing only letters!</p>
					</div>
					<div class="w-full">
						<label for="last_name" class="label">
							<span class="label-text">Last Name</span>
						</label>
						<input
							type="text"
							name="last_name"
							class="input input-bordered validator custom-input"
							required
							autocomplete="family-name"
							pattern="[A-Za-z]+"
							placeholder="Enter your last name"
						/>
						<p class="validator-hint">Must be more than 1 character containing only letters!</p>
					</div>
				</div>
				<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="username" class="label">
							<span class="label-text">Username</span>
						</label>
						<input
							type="text"
							name="username"
							class="input input-bordered validator custom-input"
							required
							pattern="[A-Za-z][A-Za-z0-9\-]*"
							minlength="3"
							maxlength="30"
							title="Only letters, numbers or dash"
							autocomplete="email"
							placeholder="Enter your username"
						/>
						<p class="validator-hint">
							Must be 3 to 30 characters containing only letters, numbers or dash!
						</p>
					</div>
				</div>
				<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="email" class="label">
							<span class="label-text">Email</span>
						</label>
						<input
							type="email"
							name="email"
							class="input input-bordered validator custom-input"
							required
							autocomplete="email"
							placeholder="Enter your email"
						/>
						<p class="validator-hint">Enter a valid email address!</p>
					</div>
				</div>
				<div class="form-control mb-2 flex flex-col gap-3 sm:flex-row">
					<div class="w-full">
						<label for="password" class="label">
							<span class="label-text">Password</span>
						</label>
						<div class="relative">
						<input
							type={showPassword ? 'text' : 'password'}
							name="password"
							class="input input-bordered validator custom-input pr-9"
							required
							minlength="8"
							autocomplete="new-password"
							placeholder="Enter your password"
						/>
						<button
								type="button"
								class="absolute inset-y-0 right-0 flex items-center pb-6 pr-3 text-sm leading-5"
								on:click={() => (showPassword = !showPassword)}
							>
								{#if showPassword}
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
					<button class="btn btn-primary text-secondary hover:bg-primary-focus w-1/5" type="submit"
						>Sign Up</button
					>
				</div>
				<p class="mt-2 text-center text-sm/6 text-base-100">
					Already a member?
					<a href="/" class="font-semibold text-primary hover:text-base-100"
						>Login</a
					>
				</p>

			</form>
		</div>
	</div>
</main>
