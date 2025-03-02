// module.exports = {
// 	purge: [],
// 	darkMode: false, // or 'media' or 'class'
// 	theme: {
// 		extend: {}
// 	},
// 	variants: {
// 		extend: {}
// 	},
// 	plugins: [require('daisyui')]
// };
module.exports = {
	content: [
		'./src/**/*.{html,js,svelte,ts}'
		// Add more paths as needed (e.g., if you have components in other directories)
	],
	darkMode: false, // or 'media' or 'class'
	theme: {
		extend: {}
	},
	variants: {
		extend: {}
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: ['light', 'dark', 'cupcake']
	}
};
