<script>
    let username = "";
    let password = "";
    let message = "";

    async function login() {
        const response = await fetch("http://127.0.0.1:8000/api/users/login/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem("token", data.access);
            message = "Login successful!";
        } else {
            message = data.message;
        }
    }
</script>

<form on:submit|preventDefault={login}>
    <input type = "text" bind:value={username} placeholder="Username" required />
    <input type = "text" bind:value={password} placeholder="password" required />
    <button type = "submit">Login</button>
    <p>{message}</p>

</form>