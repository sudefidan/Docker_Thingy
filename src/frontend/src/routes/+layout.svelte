<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<main class="main-container">
    <!-- Left panel -->
    <div class="left-panel">
        <!-- Panel content -->
        <ul>
            <li class="panel-item">
                <a href="#" class="panel-item-text">
                    <span class="ml-2">Hub</span>
                </a>
            </li>
            <li class="panel-item">
                <a href="#" class="panel-item-text">
                    <span class="ml-2">Communities</span>
                </a>
            </li>
            <li class="panel-item">
                <a href="#" class="panel-item-text">
                    <span class="ml-2">Events</span>
                </a>
            </li>
            <li class="panel-item">
                <a href="#" class="panel-item-text">
                    <span class="ml-2">Notifications</span>
                </a>
            </li>
            <li class="panel-item">
                <a href="#" class="panel-item-text">
                    <span class="ml-2">Profile</span>
                </a>
            </li>
        </ul>
    </div>

    <!-- Main content -->

	<div class="top-panel">
        <div class="p-4">
            <input type="text" placeholder="Search..." class="search-bar" />
        </div>
        <div class="main-content">
            {@render children()}
        </div>
    </div>
</main>
