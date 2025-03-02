<script>
    let name = "";
    let email = "";
    let password = "";

    async function createUser() {
    console.log("Sending POST request");
    try {
        const response = await fetch("http://127.0.0.1:8000/api/register/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: name,
                email: email,
                password: password
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error("Error:", errorData);
            alert("Error: " + errorData.error);
        } else {
            const data = await response.json();
            console.log("Success:", data);
            alert("User created successfully!");
        }
    } catch (error) {
        console.error("Request failed:", error);
    }
}
function handleSubmit(event) {
    console.log("Form submitted");
    event.preventDefault();
    createUser();
}
</script>

<main>
    <h1>Enter your details:</h1>
    <form on:submit={handleSubmit}>
        <div>
            <label for="name">Name:</label>
            <input type="text" id="name" bind:value={name} required />
        </div>

        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" bind:value={email} required />
        </div>

        <div>
            <label for="password">Password:</label>
            <input type="password" id="password" bind:value={password} required />
        </div>

        <div>
            <button type="submit">Submit</button>
        </div>
    </form>
</main>