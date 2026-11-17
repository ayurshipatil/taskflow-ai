import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  SafeAreaView,
} from "react-native";
import { authService } from "../services/api";

export function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (loginEmail?: string) => {
    const targetEmail = loginEmail || email;
    const targetPass = loginEmail ? "password123" : password;
    if (!targetEmail.trim()) return;

    setError("");
    setLoading(true);
    try {
      await authService.login(targetEmail.trim(), targetPass);
      navigation.replace("MainTabs");
    } catch (err: any) {
      setError(err.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.container}>
        {/* Brand */}
        <View style={styles.brandBox}>
          <View style={styles.logo}>
            <Text style={styles.logoText}>TF</Text>
          </View>
          <Text style={styles.title}>TaskFlow AI</Text>
          <Text style={styles.subtitle}>Mobile Enterprise Suite</Text>
        </View>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        {/* Inputs */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Email Address</Text>
          <TextInput
            style={styles.input}
            placeholder="elena@taskflow.ai"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Password</Text>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        <TouchableOpacity
          style={styles.btnPrimary}
          onPress={() => handleLogin()}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.btnText}>Sign In</Text>
          )}
        </TouchableOpacity>

        {/* 1-Click Demo Profiles */}
        <Text style={styles.demoTitle}>Quick Demo Sign In</Text>
        <View style={styles.demoGrid}>
          <TouchableOpacity
            style={styles.demoBtn}
            onPress={() => handleLogin("admin@taskflow.ai")}
          >
            <Text style={styles.demoBtnText}>👑 Admin (Elena)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.demoBtn}
            onPress={() => handleLogin("sarah.pm@taskflow.ai")}
          >
            <Text style={styles.demoBtnText}>📋 PM (Sarah)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.demoBtn}
            onPress={() => handleLogin("alex.dev@taskflow.ai")}
          >
            <Text style={styles.demoBtnText}>💻 Dev (Alex)</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.demoBtn}
            onPress={() => handleLogin("emily.team@taskflow.ai")}
          >
            <Text style={styles.demoBtnText}>🎨 Team (Emily)</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f8fafc" },
  container: { padding: 24, justifyContent: "center", minHeight: "100%" },
  brandBox: { alignItems: "center", marginBottom: 32 },
  logo: {
    width: 52,
    height: 52,
    borderRadius: 14,
    backgroundColor: "#4f46e5",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  logoText: { color: "#fff", fontSize: 20, fontWeight: "900" },
  title: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  subtitle: { fontSize: 13, color: "#64748b", marginTop: 4 },
  errorText: {
    color: "#dc2626",
    backgroundColor: "#fee2e2",
    padding: 10,
    borderRadius: 8,
    fontSize: 12,
    marginBottom: 16,
    textAlign: "center",
  },
  inputGroup: { marginBottom: 16 },
  label: { fontSize: 12, fontWeight: "600", color: "#334155", marginBottom: 6 },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    color: "#0f172a",
  },
  btnPrimary: {
    backgroundColor: "#4f46e5",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 8,
  },
  btnText: { color: "#fff", fontSize: 14, fontWeight: "700" },
  demoTitle: {
    textAlign: "center",
    fontSize: 11,
    fontWeight: "700",
    color: "#94a3b8",
    textTransform: "uppercase",
    marginTop: 32,
    marginBottom: 12,
  },
  demoGrid: { flexDirection: "row", flexWrap: "wrap", justifyContent: "space-between" },
  demoBtn: {
    width: "48%",
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
    padding: 10,
    borderRadius: 8,
    marginBottom: 8,
    alignItems: "center",
  },
  demoBtnText: { fontSize: 12, fontWeight: "600", color: "#475569" },
});
