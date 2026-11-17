import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { projectService } from "../services/api";
import { Project } from "../types";

export function ProjectsScreen({ navigation }: any) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  const loadProjects = async () => {
    try {
      const data = await projectService.getProjects();
      setProjects(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

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
        data={projects}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate("ProjectDetail", { projectId: item.id })}
          >
            <View style={styles.topRow}>
              <Text style={styles.title}>{item.name}</Text>
              <Text style={styles.status}>{item.status.toUpperCase()}</Text>
            </View>
            <Text style={styles.desc} numberOfLines={2}>
              {item.description || "No description provided"}
            </Text>

            <View style={styles.footer}>
              <Text style={styles.meta}>{item.task_count} Tasks</Text>
              <Text style={styles.progress}>{item.progress_percentage}% Done</Text>
            </View>
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
    padding: 16,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  topRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 14, fontWeight: "700", color: "#0f172a", flex: 1, marginRight: 8 },
  status: {
    fontSize: 9,
    fontWeight: "700",
    color: "#4f46e5",
    backgroundColor: "#eef2ff",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  desc: { fontSize: 12, color: "#64748b", marginVertical: 6, lineHeight: 16 },
  footer: { flexDirection: "row", justifyContent: "space-between", marginTop: 4 },
  meta: { fontSize: 11, color: "#94a3b8", fontWeight: "600" },
  progress: { fontSize: 11, color: "#10b981", fontWeight: "700" },
});
