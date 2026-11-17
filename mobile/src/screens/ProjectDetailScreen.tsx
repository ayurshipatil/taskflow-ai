import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { projectService, taskService } from "../services/api";
import { Project, Task } from "../types";

export function ProjectDetailScreen({ route, navigation }: any) {
  const { projectId } = route.params;
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [p, t] = await Promise.all([
        projectService.getProject(projectId),
        taskService.getProjectTasks(projectId),
      ]);
      setProject(p);
      setTasks(t);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  if (loading || !project) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#4f46e5" />
      </View>
    );
  }

  const columns = [
    { id: "todo", title: "To Do" },
    { id: "in_progress", title: "In Progress" },
    { id: "in_review", title: "In Review" },
    { id: "completed", title: "Completed" },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.projectCard}>
        <Text style={styles.name}>{project.name}</Text>
        <Text style={styles.desc}>{project.description}</Text>
        <Text style={styles.meta}>
          {project.task_count} Tasks • {project.progress_percentage}% Done
        </Text>
      </View>

      <View style={styles.taskSection}>
        <Text style={styles.sectionTitle}>Project Deliverables</Text>
        {tasks.map((task) => (
          <TouchableOpacity
            key={task.id}
            style={styles.taskItem}
            onPress={() => navigation.navigate("TaskDetail", { taskId: task.id })}
          >
            <View style={styles.taskHeader}>
              <Text style={styles.taskTitle}>{task.title}</Text>
              <Text style={styles.taskStatus}>{task.status.replace("_", " ")}</Text>
            </View>
            <Text style={styles.taskPriority}>{task.priority.toUpperCase()} Priority</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  projectCard: {
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    marginBottom: 16,
  },
  name: { fontSize: 16, fontWeight: "800", color: "#0f172a" },
  desc: { fontSize: 12, color: "#64748b", marginVertical: 6 },
  meta: { fontSize: 11, color: "#4f46e5", fontWeight: "700" },
  taskSection: { marginTop: 8 },
  sectionTitle: { fontSize: 14, fontWeight: "700", color: "#0f172a", marginBottom: 10 },
  taskItem: {
    backgroundColor: "#fff",
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  taskHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  taskTitle: { fontSize: 13, fontWeight: "600", color: "#1e293b", flex: 1, marginRight: 6 },
  taskStatus: {
    fontSize: 9,
    fontWeight: "700",
    color: "#4f46e5",
    backgroundColor: "#eef2ff",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    textTransform: "uppercase",
  },
  taskPriority: { fontSize: 10, color: "#94a3b8", marginTop: 4, fontWeight: "600" },
});
