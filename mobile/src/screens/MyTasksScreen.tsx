import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { taskService } from "../services/api";
import { Task } from "../types";

export function MyTasksScreen({ navigation }: any) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTasks = async () => {
    try {
      const data = await taskService.getMyTasks();
      setTasks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const toggleStatus = async (task: Task) => {
    const nextStatus = task.status === "completed" ? "todo" : "completed";
    try {
      await taskService.updateTaskStatus(task.id, nextStatus);
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: nextStatus as any } : t))
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
        data={tasks}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate("TaskDetail", { taskId: item.id })}
          >
            <TouchableOpacity
              style={[
                styles.checkbox,
                item.status === "completed" && styles.checkboxActive,
              ]}
              onPress={() => toggleStatus(item)}
            >
              {item.status === "completed" && <Text style={styles.checkMark}>✓</Text>}
            </TouchableOpacity>

            <View style={styles.cardContent}>
              <Text
                style={[
                  styles.title,
                  item.status === "completed" && styles.titleCompleted,
                ]}
              >
                {item.title}
              </Text>
              <Text style={styles.meta}>
                {item.status.replace("_", " ").toUpperCase()} • {item.priority.toUpperCase()}
              </Text>
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
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    padding: 14,
    borderRadius: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 1.5,
    borderColor: "#94a3b8",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  checkboxActive: { backgroundColor: "#10b981", borderColor: "#10b981" },
  checkMark: { color: "#fff", fontSize: 12, fontWeight: "bold" },
  cardContent: { flex: 1 },
  title: { fontSize: 13, fontWeight: "600", color: "#1e293b" },
  titleCompleted: { textDecorationLine: "line-through", color: "#94a3b8" },
  meta: { fontSize: 10, color: "#64748b", marginTop: 2, fontWeight: "600" },
});
