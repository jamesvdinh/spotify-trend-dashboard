import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Pin to IPv4 loopback: some environments resolve "localhost" to ::1 only,
    // which breaks the http://127.0.0.1:5173 redirect the backend sends after login.
    host: "127.0.0.1",
  },
});
