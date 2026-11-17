import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  RefreshControl,
} from "react-native";
import { request, taskService } from "../services/api";
import { Task, DashboardMetrics } from "../types";

export function DashboardScreen({ navigation }: any) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [m, t] = await Promise.all([
        request<DashboardMetrics>("/analytics/dashboard"),
        taskService.getMyTasks(),
      ]);
      setMetrics(m);
      setTasks(t);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#4f46e5" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); loadData(); }} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.greeting}>TaskFlow Mobile</Text>
        <Text style={styles.subGreeting}>Intelligent Sprint Tracker</Text>
      </View>

      {/* Metrics Row */}
      <View style={styles.metricRow}>
        <View style={styles.metricCard}>
          <Text style={styles.metricVal}>{metrics?.total_projects || 0}</Text>
          <Text style={styles.metricLbl}>Projects</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={[styles.metricVal, { color: "#10b981" }]}>
            {metrics?.completed_tasks || 0}
          </Text>
          <Text style={styles.metricLbl}>Completed</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={[styles.metricVal, { color: "#f59e0b" }]}>
            {metrics?.pending_tasks || 0}
          </Text>
          <Text style={styles.metricLbl}>Pending</Text>
        </View>
        <View style={styles.metricCard}>
          <Text
            style={[
              styles.metricVal,
              { color: (metrics?.overdue_tasks || 0) > 0 ? "#ef4444" : "#64748b" },
            ]}
          >
            {metrics?.overdue_tasks || 0}
          </Text>
          <Text style={styles.metricLbl}>Overdue</Text>
        </View>
      </View>

      {/* AI Quick Banner */}
      <TouchableOpacity
        style={styles.aiBanner}
        onPress={() => navigation.navigate("AIAssistant")}
      >
        <Text style={styles.aiTitle}>✨ AI Assistant Ready</Text>
        <Text style={styles.aiDesc}>
          Decompose tasks, analyze risks, and ask questions about sprint deliverables.
        </Text>
      </TouchableOpacity>

      {/* My Tasks Section */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>My Tasks ({tasks.length})</Text>
        <TouchableOpacity onPress={() => navigation.navigate("MyTasks")}>
          <Text style={styles.seeAll}>View All</Text>
        </TouchableOpacity>
      </View>

      {tasks.slice(0, 4).map((task) => (
        <TouchableOpacity
          key={task.id}
          style={styles.taskCard}
          onPress={() => navigation.navigate("TaskDetail", { taskId: task.id })}
        >
          <View style={styles.taskTop}>
            <Text style={styles.taskTitle}>{task.title}</Text>
            <Text style={styles.taskStatus}>{task.status.replace("_", " ")}</Text>
          </View>
          <Text style={styles.taskPriority}>Priority: {task.priority}</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  header: { marginBottom: 16 },
  greeting: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  subGreeting: { fontSize: 13, color: "#64748b", marginTop: 2 },
  metricRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 16 },
  metricCard: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    width: "23%",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  metricVal: { fontSize: 18, fontWeight: "800", color: "#0f172a" },
  metricLbl: { fontSize: 10, color: "#94a3b8", marginTop: 2, fontWeight: "600" },
  aiBanner: {
    backgroundColor: "#e0e7ff",
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#c7d2fe",
  },
  aiTitle: { fontSize: 13, fontWeight: "700", color: "#3730a3" },
  aiDesc: { fontSize: 11, color: "#4338ca", marginTop: 4, lineHeight: 16 },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 10,
  },
  sectionTitle: { fontSize: 14, fontWeight: "700", color: "#0f172a" },
  seeAll: { fontSize: 12, color: "#4f46e5", fontWeight: "600" },
  taskCard: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  taskTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  taskTitle: { fontSize: 13, fontWeight: "600", color: "#1e293b", flex: 1, marginRight: 8 },
  taskStatus: {
    fontSize: 10,
    fontWeight: "700",
    textTransform: "uppercase",
    color: "#4f46e5",
    backgroundColor: "#eef2ff",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  taskPriority: { fontSize: 11, color: "#64748b", marginTop: 4, textTransform: "capitalize" },
});
