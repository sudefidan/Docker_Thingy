<script>
    import HubIcon from '../../assets/hub.svg';
     let currentPage = 'hub'; // Example current page

    function isActive(page) {
        return currentPage === page ? 'icon-active' : 'icon-default';
    }
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
            <div>
                <h1 class="text-4xl font-bold mb-4">Welcome to the Homepage</h1>
                <p class="text-lg">This is the homepage with a blue background.</p>
            </div>
        </div>
    </div>
</main>