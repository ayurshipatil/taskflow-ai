import React from "react";
import { View, Text, TouchableOpacity, StyleSheet } from "react-native";
import { clearToken, getCurrentUser } from "../services/api";

export function ProfileScreen({ navigation }: any) {
  const user = getCurrentUser();

  const handleLogout = () => {
    clearToken();
    navigation.replace("Login");
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{user?.full_name?.charAt(0) || "U"}</Text>
        </View>

        <Text style={styles.name}>{user?.full_name || "Elena Vance"}</Text>
        <Text style={styles.email}>{user?.email || "admin@taskflow.ai"}</Text>

        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{user?.role?.replace("_", " ").toUpperCase() || "ADMIN"}</Text>
        </View>
      </View>

      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutText}>Sign Out</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 16,
    padding: 24,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    marginBottom: 20,
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: "#4f46e5",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  avatarText: { color: "#fff", fontSize: 24, fontWeight: "900" },
  name: { fontSize: 16, fontWeight: "800", color: "#0f172a" },
  email: { fontSize: 12, color: "#64748b", marginTop: 2 },
  roleBadge: {
    backgroundColor: "#eef2ff",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
    marginTop: 12,
  },
  roleText: { color: "#4f46e5", fontSize: 10, fontWeight: "700" },
  logoutBtn: {
    backgroundColor: "#fee2e2",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  logoutText: { color: "#dc2626", fontWeight: "700", fontSize: 13 },
});
