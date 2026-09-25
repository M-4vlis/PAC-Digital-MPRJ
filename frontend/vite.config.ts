import { defineConfig } from 'vite'
export default defineConfig({esbuild:{jsx:'automatic',jsxDev:false}, server:{proxy:{'/api':'http://localhost:8000','/health':'http://localhost:8000'}}})
