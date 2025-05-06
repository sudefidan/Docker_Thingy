import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Enable svelte preprocessing (e.g. PostCSS, TypeScript, etc.)
  preprocess: vitePreprocess(),

  kit: {
    // Use the static-site adapter
    adapter: adapter({
      // default options are usually fine
      pages: 'build',
      assets: 'build',
      fallback: null
    }),

    // If you have any prerendered pages, list them here,
    // or use `entries: ['*']` to prerender everything.
    prerender: {
      entries: []
    }
  }
};

export default {
	kit: {
	  adapter: adapter(),
	}
  };
