/**
 * CameraScreen — the main screen the factory worker sees.
 *
 * WHAT THIS SCREEN DOES:
 *   1. Shows a camera preview (or a "pick image" button on web)
 *   2. User taps "Capture" to take a photo
 *   3. The photo is sent to POST /api/detect on the server
 *   4. The server runs YOLO detection and returns results
 *   5. Results are passed to ResultScreen for display
 *
 * WHY TWO CAPTURE METHODS:
 *   - On a phone with a native app: expo-camera gives a live preview
 *   - On web (our primary mode): expo-image-picker lets the user
 *     take a photo or select one from their gallery
 *   We support both so the app works in any context.
 */

import React, { useState } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
  Image,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import { detectImage, checkHealth } from "../services/api";

export default function CameraScreen({ navigation }) {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [serverStatus, setServerStatus] = useState(null);

  // ── Check server connection ─────────────────────────────────────────
  React.useEffect(() => {
    checkHealth().then((ok) => setServerStatus(ok));
  }, []);

  // ── Take a photo using the device camera ────────────────────────────
  const takePhoto = async () => {
    try {
      // Request camera permission
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "Permission Needed",
          "Camera access is required to scan safety equipment."
        );
        return;
      }

      // Launch camera
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ["images"],
        quality: 0.8, // 80% quality — balance between size and clarity
        base64: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const imageUri = result.assets[0].uri;
        setPreview(imageUri);
        await sendForDetection(imageUri);
      }
    } catch (error) {
      Alert.alert("Error", `Camera failed: ${error.message}`);
    }
  };

  // ── Pick an image from gallery ──────────────────────────────────────
  const pickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== "granted") {
        Alert.alert(
          "Permission Needed",
          "Photo library access is required to select images."
        );
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ["images"],
        quality: 0.8,
        base64: false,
      });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const imageUri = result.assets[0].uri;
        setPreview(imageUri);
        await sendForDetection(imageUri);
      }
    } catch (error) {
      Alert.alert("Error", `Image picker failed: ${error.message}`);
    }
  };

  // ── Send image to server for detection ──────────────────────────────
  const sendForDetection = async (imageUri) => {
    setLoading(true);
    try {
      const response = await detectImage(imageUri);

      // Navigate to ResultScreen with the detection results and the image
      navigation.navigate("Results", {
        detections: response.detections,
        count: response.count,
        imageUri: imageUri,
      });
    } catch (error) {
      Alert.alert(
        "Detection Failed",
        `Could not detect objects: ${error.message}\n\nMake sure the server is running.`
      );
    } finally {
      setLoading(false);
    }
  };

  // ── UI ──────────────────────────────────────────────────────────────
  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Safety-First Auditor</Text>
        <Text style={styles.subtitle}>Scan PPE equipment for inventory</Text>
        <View style={styles.statusRow}>
          <View
            style={[
              styles.statusDot,
              { backgroundColor: serverStatus ? "#4CAF50" : "#f44336" },
            ]}
          />
          <Text style={styles.statusText}>
            {serverStatus === null
              ? "Checking server..."
              : serverStatus
              ? "Server connected"
              : "Server offline"}
          </Text>
        </View>
      </View>

      {/* Image preview area */}
      <View style={styles.previewContainer}>
        {preview ? (
          <Image source={{ uri: preview }} style={styles.previewImage} />
        ) : (
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>No image selected</Text>
            <Text style={styles.placeholderSubtext}>
              Take a photo or pick one from your gallery
            </Text>
          </View>
        )}
      </View>

      {/* Loading indicator */}
      {loading && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#FFD700" />
          <Text style={styles.loadingText}>Detecting PPE...</Text>
        </View>
      )}

      {/* Action buttons */}
      {!loading && (
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.cameraButton]}
            onPress={takePhoto}
          >
            <Text style={styles.buttonText}>Take Photo</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.galleryButton]}
            onPress={pickImage}
          >
            <Text style={styles.buttonText}>Pick from Gallery</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.historyButton]}
            onPress={() => navigation.navigate("History")}
          >
            <Text style={styles.buttonText}>View History</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
    paddingTop: Platform.OS === "web" ? 20 : 50,
  },
  header: {
    alignItems: "center",
    paddingVertical: 15,
  },
  title: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#FFD700",
  },
  subtitle: {
    fontSize: 14,
    color: "#aaa",
    marginTop: 4,
  },
  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6,
  },
  statusText: {
    color: "#ccc",
    fontSize: 12,
  },
  previewContainer: {
    flex: 1,
    margin: 16,
    borderRadius: 12,
    overflow: "hidden",
    backgroundColor: "#16213e",
    justifyContent: "center",
    alignItems: "center",
  },
  previewImage: {
    width: "100%",
    height: "100%",
    resizeMode: "contain",
  },
  placeholder: {
    alignItems: "center",
    padding: 40,
  },
  placeholderText: {
    fontSize: 18,
    color: "#666",
    marginBottom: 8,
  },
  placeholderSubtext: {
    fontSize: 13,
    color: "#444",
    textAlign: "center",
  },
  loadingContainer: {
    alignItems: "center",
    paddingVertical: 20,
  },
  loadingText: {
    color: "#FFD700",
    marginTop: 10,
    fontSize: 16,
  },
  buttonContainer: {
    paddingHorizontal: 16,
    paddingBottom: Platform.OS === "web" ? 20 : 40,
    gap: 10,
  },
  button: {
    paddingVertical: 16,
    borderRadius: 10,
    alignItems: "center",
  },
  cameraButton: {
    backgroundColor: "#FFD700",
  },
  galleryButton: {
    backgroundColor: "#0f3460",
    borderWidth: 1,
    borderColor: "#FFD700",
  },
  historyButton: {
    backgroundColor: "#16213e",
    borderWidth: 1,
    borderColor: "#444",
  },
  buttonText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#fff",
  },
});
