// svelte.dev/docs/kit/adapter-static
import adapter from '@sveltejs/adapter-static';

// svelte.dev/docs/kit/integrations
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default { 
    preprocess: [vitePreprocess()],
    
    kit: { 
        adapter: adapter({ 
            pages: 'build', 
            assets: 'build',
            fallback: undefined,
            precompress: false,
            strict: true
        }),
    } 
};

