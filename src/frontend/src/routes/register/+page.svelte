<script lang="ts">
	import { enhance } from '$app/forms';

	let registerForm: HTMLFormElement;

	interface CustomResult {
		message?: string;
		error?: string;
	}
</script>

<main>
	<h1>Enter your details:</h1>
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
	>
		<label for="first_name">First Name:</label>
		<input type="text" name="first_name" required />
		<label for="last_name">Last Name:</label>
		<input type="text" name="last_name" required />
		<label for="username">Username:</label>
		<input type="text" name="username" required />
		<label for="email">Email:</label>
		<input type="email" name="email" required />
		<label for="password">Password:</label>
		<input type="password" name="password" required />
		<button class="btn btn-primary" type="submit">Submit</button>
	</form>
</main>
