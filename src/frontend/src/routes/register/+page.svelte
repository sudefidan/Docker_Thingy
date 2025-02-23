<style>

</style>

<main>

    <h1>Enter your details:</h1>
    <form action="/submit" method="POST">
        <div>
            <label for="username">Name:</label>
            <input type="text" id="name" name="name" required />
        </div>

        <div>
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required />
        </div>

        <div>
            <button type="submit">Submit</button>
        </div>
    </form>
</main>

