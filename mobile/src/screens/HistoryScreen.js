/**
 * HistoryScreen — shows past detection logs from the inventory database.
 *
 * WHAT THIS SCREEN DOES:
 *   1. Fetches the latest inventory logs from GET /api/inventory
 *   2. Displays them as a scrollable list with timestamps and confidence
 *   3. Pull-to-refresh to reload the list
 *
 * WHY THIS SCREEN EXISTS:
 *   The factory floor supervisor needs to see what has been scanned.
 *   This screen proves the full pipeline works: camera → detection → database → display.
 *   In the interview, you can show detections appearing here in real-time
 *   after scanning an item.
 *
 * CONNECTIONS:
 *   - Calls api.js → getInventoryLogs() → GET /api/inventory
 *   - Calls api.js → getItems() → GET /api/items (to show item names)
 */

import React, { useState, useEffect, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Platform,
  RefreshControl,
} from "react-native";
import { getInventoryLogs, getItems } from "../services/api";

export default function HistoryScreen({ navigation }) {
  const [logs, setLogs] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // ── Fetch data ──────────────────────────────────────────────────────
  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [logsData, itemsData] = await Promise.all([
        getInventoryLogs(50),
        getItems(),
      ]);
      setLogs(logsData);
      setItems(itemsData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Pull-to-refresh ─────────────────────────────────────────────────
  const onRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  // ── Map item_id to item name ────────────────────────────────────────
  const getItemName = (itemId) => {
    const item = items.find((i) => i.id === itemId);
    return item ? item.name : `Item #${itemId}`;
  };

  // ── Format timestamp ────────────────────────────────────────────────
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  // ── Get confidence color ────────────────────────────────────────────
  const getConfidenceColor = (conf) => {
    if (conf >= 0.8) return "#4CAF50";
    if (conf >= 0.6) return "#FFD700";
    return "#f44336";
  };

  // ── Render a single log entry ───────────────────────────────────────
  const renderLogItem = ({ item: log }) => (
    <View style={styles.logCard}>
      <View style={styles.logHeader}>
        <Text style={styles.logItemName}>{getItemName(log.item_id)}</Text>
        <Text
          style={[
            styles.logConfidence,
            { color: getConfidenceColor(log.confidence) },
          ]}
        >
          {(log.confidence * 100).toFixed(1)}%
        </Text>
      </View>
      <Text style={styles.logDate}>{formatDate(log.detected_at)}</Text>
      {log.notes && <Text style={styles.logNotes}>{log.notes}</Text>}
    </View>
  );

  // ── UI ──────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <View style={[styles.container, styles.centered]}>
        <ActivityIndicator size="large" color="#FFD700" />
        <Text style={styles.loadingText}>Loading history...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.errorText}>Could not load history</Text>
        <Text style={styles.errorDetail}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={fetchData}>
          <Text style={styles.retryText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Detection History</Text>
        <Text style={styles.countText}>{logs.length} entries</Text>
      </View>

      {logs.length === 0 ? (
        <View style={styles.centered}>
          <Text style={styles.emptyText}>No detections yet</Text>
          <Text style={styles.emptySubtext}>
            Scan some safety equipment to see entries here.
          </Text>
          <TouchableOpacity
            style={styles.scanButton}
            onPress={() => navigation.navigate("Camera")}
          >
            <Text style={styles.scanButtonText}>Start Scanning</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={logs}
          renderItem={renderLogItem}
          keyExtractor={(item) => item.id.toString()}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              tintColor="#FFD700"
            />
          }
          contentContainerStyle={styles.listContent}
        />
      )}
    </View>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#1a1a2e",
  },
  centered: {
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  header: {
    padding: 16,
    alignItems: "center",
    borderBottomWidth: 1,
    borderBottomColor: "#16213e",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#FFD700",
  },
  countText: {
    fontSize: 13,
    color: "#888",
    marginTop: 4,
  },
  listContent: {
    padding: 16,
    paddingBottom: Platform.OS === "web" ? 30 : 50,
  },
  logCard: {
    backgroundColor: "#16213e",
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    borderLeftWidth: 3,
    borderLeftColor: "#FFD700",
  },
  logHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  logItemName: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#fff",
  },
  logConfidence: {
    fontSize: 16,
    fontWeight: "bold",
  },
  logDate: {
    fontSize: 12,
    color: "#888",
    marginTop: 4,
  },
  logNotes: {
    fontSize: 12,
    color: "#666",
    marginTop: 6,
    fontStyle: "italic",
  },
  loadingText: {
    color: "#FFD700",
    marginTop: 10,
  },
  errorText: {
    color: "#f44336",
    fontSize: 18,
    fontWeight: "bold",
  },
  errorDetail: {
    color: "#888",
    fontSize: 13,
    marginTop: 6,
    textAlign: "center",
  },
  retryButton: {
    marginTop: 16,
    paddingHorizontal: 24,
    paddingVertical: 10,
    backgroundColor: "#0f3460",
    borderRadius: 8,
  },
  retryText: {
    color: "#FFD700",
    fontWeight: "bold",
  },
  emptyText: {
    color: "#888",
    fontSize: 18,
    marginBottom: 8,
  },
  emptySubtext: {
    color: "#555",
    fontSize: 13,
    textAlign: "center",
    marginBottom: 20,
  },
  scanButton: {
    paddingHorizontal: 24,
    paddingVertical: 12,
    backgroundColor: "#FFD700",
    borderRadius: 8,
  },
  scanButtonText: {
    color: "#1a1a2e",
    fontWeight: "bold",
    fontSize: 15,
  },
});
