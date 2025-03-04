<script lang="ts">
	import { enhance } from '$app/forms';

	let registerForm: HTMLFormElement;

	interface CustomResult {
		message?: string;
		error?: string;
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
						// Not getting expected SvelteKit response as Django is responding, not SvelteKit. We either send a message or an error.
						const customResult = result as CustomResult;
						if (customResult?.message) {
							alert(customResult.message);
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
							class="input input-bordered validator focus:outline-primary bg-secondary text-base-100 w-full rounded-md focus:outline-2 focus:-outline-offset-2"
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
							class="input input-bordered validator focus:outline-primary bg-secondary text-base-100 w-full rounded-md focus:outline-2 focus:-outline-offset-2"
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
							class="input input-bordered validator focus:outline-primary bg-secondary text-base-100 w-full rounded-md focus:outline-2 focus:-outline-offset-2"
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
							class="input input-bordered validator focus:outline-primary bg-secondary text-base-100 w-full rounded-md focus:outline-2 focus:-outline-offset-2"
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
						<input
							type="password"
							name="password"
							class="input input-bordered validator focus:outline-primary bg-secondary text-base-100 w-full rounded-md focus:outline-2 focus:-outline-offset-2"
							required
							minlength="8"
							autocomplete="new-password"
							placeholder="Enter your password"
						/>
						<p class="validator-hint">Must be more than 8 characters!</p>
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
