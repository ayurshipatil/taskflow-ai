import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { aiService } from "../services/api";

export function AIAssistantScreen() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([
    {
      id: "1",
      sender: "ai",
      text: "👋 Hi! I am TaskFlow Mobile AI. Ask me about sprint priorities, overdue tasks, or project health.",
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async (customMsg?: string) => {
    const text = customMsg || query;
    if (!text.trim() || loading) return;

    const userMsg = { id: Date.now().toString(), sender: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const res = await aiService.chat(text);
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), sender: "ai", text: res.reply },
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        { id: (Date.now() + 1).toString(), sender: "ai", text: `Error: ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Quick Prompts */}
      <View style={styles.promptBar}>
        {["What should I work on next?", "Which tasks are overdue?", "Summarise my current project"].map(
          (p) => (
            <TouchableOpacity
              key={p}
              style={styles.promptPill}
              onPress={() => handleSend(p)}
            >
              <Text style={styles.promptText}>{p}</Text>
            </TouchableOpacity>
          )
        )}
      </View>

      {/* Chat Messages */}
      <ScrollView style={styles.chatFeed}>
        {messages.map((m) => (
          <View
            key={m.id}
            style={[
              styles.msgBox,
              m.sender === "user" ? styles.msgUser : styles.msgAI,
            ]}
          >
            <Text
              style={[
                styles.msgText,
                m.sender === "user" ? styles.msgTextUser : styles.msgTextAI,
              ]}
            >
              {m.text}
            </Text>
          </View>
        ))}
        {loading && (
          <View style={styles.loadingBox}>
            <ActivityIndicator size="small" color="#4f46e5" />
            <Text style={styles.loadingText}>AI formulating reply...</Text>
          </View>
        )}
      </ScrollView>

      {/* Input */}
      <View style={styles.inputRow}>
        <TextInput
          style={styles.input}
          placeholder="Ask TaskFlow AI..."
          value={query}
          onChangeText={setQuery}
        />
        <TouchableOpacity
          style={styles.sendBtn}
          onPress={() => handleSend()}
          disabled={loading}
        >
          <Text style={styles.sendText}>Send</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  promptBar: { padding: 10, flexDirection: "row", flexWrap: "wrap", gap: 6, backgroundColor: "#fff" },
  promptPill: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    backgroundColor: "#eef2ff",
    borderWidth: 1,
    borderColor: "#c7d2fe",
  },
  promptText: { fontSize: 10, color: "#4f46e5", fontWeight: "600" },
  chatFeed: { flex: 1, padding: 14 },
  msgBox: { padding: 12, borderRadius: 12, marginBottom: 8, maxWidth: "85%" },
  msgUser: { alignSelf: "flex-end", backgroundColor: "#4f46e5" },
  msgAI: { alignSelf: "flex-start", backgroundColor: "#fff", borderWidth: 1, borderColor: "#e2e8f0" },
  msgText: { fontSize: 13, lineHeight: 18 },
  msgTextUser: { color: "#fff" },
  msgTextAI: { color: "#1e293b" },
  loadingBox: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 6 },
  loadingText: { fontSize: 11, color: "#64748b", fontStyle: "italic" },
  inputRow: { flexDirection: "row", padding: 10, backgroundColor: "#fff", borderTopWidth: 1, borderTopColor: "#e2e8f0" },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 13,
  },
  sendBtn: {
    backgroundColor: "#4f46e5",
    paddingHorizontal: 16,
    borderRadius: 8,
    justifyContent: "center",
    marginLeft: 8,
  },
  sendText: { color: "#fff", fontWeight: "700", fontSize: 13 },
});
