/**
 * ResultScreen — displays YOLO detection results after a photo is analyzed.
 *
 * WHAT THIS SCREEN DOES:
 *   1. Receives detection results and the image from CameraScreen
 *   2. Shows the image with a list of detected objects
 *   3. For each detection: class name, confidence percentage, bounding box
 *   4. "Save to Inventory" button sends each detection to POST /api/inventory
 *   5. Shows confirmation when the database is updated
 *
 * CONNECTIONS:
 *   - Receives data from CameraScreen via navigation params
 *   - Calls api.js → logDetection() → POST /api/inventory
 *   - Calls api.js → getItems() → GET /api/items (to map class_name → item_id)
 */

import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Image,
  Alert,
  ActivityIndicator,
  Platform,
} from "react-native";
import { logDetection, getItems } from "../services/api";

export default function ResultScreen({ route, navigation }) {
  const { detections, count, imageUri } = route.params;
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [items, setItems] = useState([]);

  // ── Fetch items list to map class_name → item_id ────────────────────
  useEffect(() => {
    getItems()
      .then(setItems)
      .catch((err) => console.log("Could not fetch items:", err.message));
  }, []);

  // ── Map class_name to item_id ───────────────────────────────────────
  const getItemId = (className) => {
    // Try to find an item whose name matches the detection class name
    // The items table should have entries like: {id: 1, name: "Hardhat"}
    const match = items.find(
      (item) => item.name.toLowerCase() === className.toLowerCase()
    );
    return match ? match.id : null;
  };

  // ── Get color for confidence score ──────────────────────────────────
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return "#4CAF50"; // Green — high confidence
    if (conf >= 0.6) return "#FFD700"; // Yellow — medium confidence
    return "#f44336"; // Red — low confidence
  };

  // ── Save all detections to the database ─────────────────────────────
  const saveToInventory = async () => {
    setSaving(true);
    let successCount = 0;
    let failCount = 0;

    for (const detection of detections) {
      const itemId = getItemId(detection.class_name);

      if (!itemId) {
        failCount++;
        continue;
      }

      try {
        await logDetection({
          item_id: itemId,
          confidence: detection.confidence,
          quantity: 1,
          notes: `Auto-detected via mobile app. Confidence: ${(
            detection.confidence * 100
          ).toFixed(1)}%`,
        });
        successCount++;
      } catch (error) {
        failCount++;
        console.log(`Failed to log ${detection.class_name}:`, error.message);
      }
    }

    setSaving(false);
    setSaved(true);

    if (failCount > 0) {
      Alert.alert(
        "Partial Save",
        `${successCount} detections saved, ${failCount} failed.\n\n` +
          "Failures may be because the item does not exist in the database yet. " +
          "Add items via the API first: POST /api/items"
      );
    } else {
      Alert.alert(
        "Database Updated!",
        `${successCount} detection(s) saved to inventory.`
      );
    }
  };

  // ── UI ──────────────────────────────────────────────────────────────
  return (
    <ScrollView style={styles.container}>
      {/* Image preview */}
      {imageUri && (
        <Image source={{ uri: imageUri }} style={styles.image} />
      )}

      {/* Results header */}
      <View style={styles.resultHeader}>
        <Text style={styles.title}>Detection Results</Text>
        <Text style={styles.countText}>
          {count} object{count !== 1 ? "s" : ""} detected
        </Text>
      </View>

      {/* Detection list */}
      {detections.length === 0 ? (
        <View style={styles.noResults}>
          <Text style={styles.noResultsText}>
            No safety equipment detected in this image.
          </Text>
          <Text style={styles.noResultsSubtext}>
            Try pointing the camera at a hardhat, safety vest, or person wearing PPE.
          </Text>
        </View>
      ) : (
        detections.map((det, index) => (
          <View key={index} style={styles.detectionCard}>
            <View style={styles.detectionHeader}>
              <Text style={styles.className}>{det.class_name}</Text>
              <Text
                style={[
                  styles.confidence,
                  { color: getConfidenceColor(det.confidence) },
                ]}
              >
                {(det.confidence * 100).toFixed(1)}%
              </Text>
            </View>
            <Text style={styles.bboxText}>
              Box: ({det.bbox.x1.toFixed(0)}, {det.bbox.y1.toFixed(0)}) to (
              {det.bbox.x2.toFixed(0)}, {det.bbox.y2.toFixed(0)})
            </Text>
          </View>
        ))
      )}

      {/* Action buttons */}
      <View style={styles.buttonContainer}>
        {detections.length > 0 && !saved && (
          <TouchableOpacity
            style={[styles.button, styles.saveButton]}
            onPress={saveToInventory}
            disabled={saving}
          >
            {saving ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Save to Inventory</Text>
            )}
          </TouchableOpacity>
        )}

        {saved && (
          <View style={styles.savedBanner}>
            <Text style={styles.savedText}>Saved to Database</Text>
          </View>
        )}

        <TouchableOpacity
          style={[styles.button, styles.newScanButton]}
          onPress={() => navigation.navigate("Camera")}
        >
          <Text style={styles.buttonText}>New Scan</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
  },
  image: {
    width: "100%",
    height: 300,
    resizeMode: "contain",
    backgroundColor: "#000",
  },
  resultHeader: {
    padding: 16,
    alignItems: "center",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#FFD700",
  },
  countText: {
    fontSize: 14,
    color: "#aaa",
    marginTop: 4,
  },
  noResults: {
    padding: 30,
    alignItems: "center",
  },
  noResultsText: {
    fontSize: 16,
    color: "#888",
    textAlign: "center",
  },
  noResultsSubtext: {
    fontSize: 13,
    color: "#555",
    textAlign: "center",
    marginTop: 8,
  },
  detectionCard: {
    marginHorizontal: 16,
    marginBottom: 10,
    padding: 16,
    backgroundColor: "#16213e",
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: "#FFD700",
  },
  detectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  className: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#fff",
  },
  confidence: {
    fontSize: 18,
    fontWeight: "bold",
  },
  bboxText: {
    fontSize: 12,
    color: "#666",
    marginTop: 6,
  },
  buttonContainer: {
    padding: 16,
    paddingBottom: Platform.OS === "web" ? 30 : 50,
    gap: 10,
  },
  button: {
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: "center",
  },
  saveButton: {
    backgroundColor: "#4CAF50",
  },
  newScanButton: {
    backgroundColor: "#0f3460",
    borderWidth: 1,
    borderColor: "#FFD700",
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#fff",
  },
  savedBanner: {
    backgroundColor: "#2e7d32",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  savedText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#fff",
  },
});
