/**
 * API configuration — controls where the mobile app sends requests.
 *
 * WHAT THIS FILE DOES:
 *   Defines the base URL for all API calls.
 *   Toggle between local development and Railway production.
 *
 * HOW TO USE:
 *   - For local development: set API_BASE_URL to your laptop's IP
 *   - For Railway deployment: set API_BASE_URL to your Railway URL
 *
 * WHY NOT localhost:
 *   When the Expo web app runs on your phone's browser,
 *   "localhost" refers to the PHONE itself, not your laptop.
 *   You need your laptop's local network IP (e.g., 192.168.1.50)
 *   or the Railway public URL.
 */

// ── Toggle this for local vs production ─────────────────────────────────

// For local development (replace with your laptop's IP):
// const API_BASE_URL = "http://192.168.1.50:8000";

// For Railway production (replace with your Railway URL):
const API_BASE_URL = "https://your-app.up.railway.app";

export default API_BASE_URL;
