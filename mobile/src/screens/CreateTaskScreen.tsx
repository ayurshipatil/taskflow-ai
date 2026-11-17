import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { taskService, projectService } from "../services/api";
import { Project } from "../types";

export function CreateTaskScreen({ navigation }: any) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [hours, setHours] = useState("4");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    projectService.getProjects().then((p) => {
      setProjects(p);
      if (p.length > 0) setSelectedProjectId(p[0].id);
    });
  }, []);

  const handleCreate = async () => {
    if (!title.trim() || !selectedProjectId) return;
    setLoading(true);
    try {
      await taskService.createTask({
        project_id: selectedProjectId,
        title: title.trim(),
        description: description.trim(),
        status: "todo",
        priority: "medium",
        estimated_hours: Number(hours) || 4,
      });
      navigation.goBack();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>New Task</Text>

      <Text style={styles.label}>Select Project</Text>
      <View style={styles.projectPills}>
        {projects.map((p) => (
          <TouchableOpacity
            key={p.id}
            style={[
              styles.pill,
              selectedProjectId === p.id && styles.pillActive,
            ]}
            onPress={() => setSelectedProjectId(p.id)}
          >
            <Text
              style={[
                styles.pillText,
                selectedProjectId === p.id && styles.pillTextActive,
              ]}
            >
              {p.name}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Task Title</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. Build authentication endpoints"
        value={title}
        onChangeText={setTitle}
      />

      <Text style={styles.label}>Description</Text>
      <TextInput
        style={[styles.input, { height: 80 }]}
        placeholder="Details and criteria..."
        multiline
        value={description}
        onChangeText={setDescription}
      />

      <Text style={styles.label}>Estimated Effort (Hours)</Text>
      <TextInput
        style={styles.input}
        keyboardType="numeric"
        value={hours}
        onChangeText={setHours}
      />

      <TouchableOpacity
        style={styles.submitBtn}
        onPress={handleCreate}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitText}>Create Task</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  header: { fontSize: 18, fontWeight: "800", color: "#0f172a", marginBottom: 16 },
  label: { fontSize: 12, fontWeight: "700", color: "#475569", marginBottom: 6 },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    padding: 10,
    fontSize: 13,
    marginBottom: 14,
  },
  projectPills: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 14 },
  pill: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: "#f1f5f9",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  pillActive: { backgroundColor: "#4f46e5", borderColor: "#4f46e5" },
  pillText: { fontSize: 11, fontWeight: "600", color: "#475569" },
  pillTextActive: { color: "#fff" },
  submitBtn: {
    backgroundColor: "#4f46e5",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  submitText: { color: "#fff", fontWeight: "700", fontSize: 14 },
});
