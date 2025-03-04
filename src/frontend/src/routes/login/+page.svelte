<script>
    let username = "";
    let password = "";
    let message = "";

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
                message = "Login successful!";
                // Optionally, handle redirection or state updates here
            } else {
                const data = await res.json();
                message = data.error || "Login failed. Please try again.";
            }
        } catch (error) {
            console.error(error);
            message = "An error occurred. Please try again.";
        }
    }
</script>

<form on:submit|preventDefault={login}>
    <input type="text" bind:value={username} placeholder="Username" required />
    <input type="password" bind:value={password} placeholder="Password" required />
    <button type="submit">Login</button>
    <p>{message}</p>
</form>