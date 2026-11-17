import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { notifService } from "../services/api";
import { Notification } from "../types";

export function NotificationsScreen() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const loadNotifs = async () => {
    try {
      const data = await notifService.getNotifications();
      setNotifications(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifs();
  }, []);

  const handleMarkRead = async (id: string) => {
    try {
      await notifService.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#4f46e5" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.card,
              !item.is_read && styles.unreadCard,
            ]}
            onPress={() => !item.is_read && handleMarkRead(item.id)}
          >
            <View style={styles.topRow}>
              <Text style={styles.title}>{item.title}</Text>
              {!item.is_read && <View style={styles.dot} />}
            </View>
            <Text style={styles.msg}>{item.message}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  card: {
    backgroundColor: "#fff",
    padding: 14,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  unreadCard: { backgroundColor: "#eef2ff", borderColor: "#c7d2fe" },
  topRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 13, fontWeight: "700", color: "#0f172a" },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#4f46e5" },
  msg: { fontSize: 12, color: "#64748b", marginTop: 4, lineHeight: 16 },
});
