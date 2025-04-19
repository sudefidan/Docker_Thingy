<script>
    export let size = 24; // Default size of the icon
    export let strokeWidth = 1.5; // Default stroke width
    export let color = "currentColor"; // Default color (inherits from parent)
</script>

<svg
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    viewBox="0 0 24 24"
    stroke-width={strokeWidth}
    stroke={color}
    width={size}
    height={size}
>
    <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M15 12H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"
    />
</svg>