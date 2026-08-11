import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';


export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  ssr: {
    noExternal: [
      '@lucide/svelte', 
      'bits-ui', 
      'tailwind-variants', 
      'tailwind-merge', 
      'date-fns',
      'svelte-dnd-action',
      'store2',
    ]
  },
  server: {
    fs: {
      strict: false,
    },
    hmr: {
      overlay: false
    }
  }
})

