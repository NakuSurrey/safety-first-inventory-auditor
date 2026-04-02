/**
 * API service — all HTTP calls to the FastAPI backend live here.
 *
 * WHAT THIS FILE DOES:
 *   Provides functions that the screens call to talk to the backend.
 *   Every function sends an HTTP request and returns the JSON response.
 *
 * WHY ONE FILE:
 *   All API calls in one place. If the URL or headers change,
 *   we change it here once — not in every screen.
 *
 * CONNECTIONS:
 *   - CameraScreen.js calls detectImage() to upload a photo
 *   - ResultScreen.js calls logDetection() to save detections to the database
 *   - HistoryScreen.js calls getInventoryLogs() to fetch past detections
 *   - All functions use API_BASE_URL from config.js
 */

import API_BASE_URL from "../config";

/**
 * Upload an image to the server for YOLO detection.
 *
 * WHAT IT DOES:
 *   Sends the photo as multipart form data to POST /api/detect.
 *   The server runs YOLOv8-nano on the image and returns detections.
 *
 * WHAT IT RETURNS:
 *   { detections: [{class_name, class_id, confidence, bbox}], count: N }
 */
export async function detectImage(imageUri) {
  // Create a FormData object — this is how browsers send files over HTTP
  const formData = new FormData();

  // For web: fetch the image URI and convert to a Blob (binary data)
  // For native: React Native handles URI-to-file conversion automatically
  const response = await fetch(imageUri);
  const blob = await response.blob();

  formData.append("file", blob, "capture.jpg");

  const result = await fetch(`${API_BASE_URL}/api/detect/`, {
    method: "POST",
    body: formData,
    // Do NOT set Content-Type header — the browser sets it automatically
    // with the correct multipart boundary string
  });

  if (!result.ok) {
    const error = await result.json().catch(() => ({ detail: "Detection failed" }));
    throw new Error(error.detail || `Server error: ${result.status}`);
  }

  return await result.json();
}

/**
 * Log a detection event to the inventory database.
 *
 * WHAT IT DOES:
 *   Sends a POST request to /api/inventory with the detection data.
 *   The server validates the data and writes it to PostgreSQL.
 *
 * WHAT IT SENDS:
 *   { item_id: 1, confidence: 0.94, location_id: null, quantity: 1 }
 */
export async function logDetection(detectionData) {
  const result = await fetch(`${API_BASE_URL}/api/inventory/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(detectionData),
  });

  if (!result.ok) {
    const error = await result.json().catch(() => ({ detail: "Failed to log detection" }));
    throw new Error(error.detail || `Server error: ${result.status}`);
  }

  return await result.json();
}

/**
 * Fetch the list of safety items from the database.
 *
 * WHAT IT DOES:
 *   Sends a GET request to /api/items.
 *   Returns the master list of items (Hardhat, Safety-Vest, Person).
 *   The mobile app uses this to map class_name → item_id.
 *
 * WHY WE NEED THIS:
 *   The detection returns class_name ("Hardhat").
 *   The inventory endpoint needs item_id (1).
 *   This function fetches the mapping.
 */
export async function getItems() {
  const result = await fetch(`${API_BASE_URL}/api/items/`);

  if (!result.ok) {
    throw new Error(`Failed to fetch items: ${result.status}`);
  }

  return await result.json();
}

/**
 * Fetch past detection logs from the inventory.
 *
 * WHAT IT DOES:
 *   Sends a GET request to /api/inventory.
 *   Returns a list of past detections with timestamps and confidence scores.
 *   Used by HistoryScreen to show what has been detected.
 */
export async function getInventoryLogs(limit = 50) {
  const result = await fetch(`${API_BASE_URL}/api/inventory/?limit=${limit}`);

  if (!result.ok) {
    throw new Error(`Failed to fetch inventory logs: ${result.status}`);
  }

  return await result.json();
}

/**
 * Check if the backend server is reachable.
 *
 * WHAT IT DOES:
 *   Sends a GET request to /health.
 *   Returns true if the server responds, false otherwise.
 */
export async function checkHealth() {
  try {
    const result = await fetch(`${API_BASE_URL}/health`);
    return result.ok;
  } catch {
    return false;
  }
}
