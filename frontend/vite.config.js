import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "localhost",
    port: 5173,
    proxy: {
      "/socket.io": {
        target: "http://localhost:5000",
        ws: true,
        changeOrigin: true,
        secure: false,

        // IMPORTANT: forward cookies to Flask
        configure: (proxy) => {
          proxy.on("proxyReq", (proxyReq, req) => {
            if (req.headers.cookie) {
              proxyReq.setHeader("cookie", req.headers.cookie);
            }
          });
        },
      },

      "/api": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/register": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/login": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/logout": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/google_login": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
      "/dashboard": {
        target: "http://localhost:5000",
        changeOrigin: true,
      },
    },
  },
});
