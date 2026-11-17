import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import { taskService } from "../services/api";
import { Task } from "../types";

export function TaskDetailScreen({ route, navigation }: any) {
  const { taskId } = route.params;
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState("");
  const [comments, setComments] = useState<any[]>([]);

  const loadTask = async () => {
    try {
      const data = await taskService.getTaskDetail(taskId);
      setTask(data);
      setComments((data as any).comments || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTask();
  }, [taskId]);

  const handleToggleSubtask = async (subtaskId: string) => {
    try {
      await taskService.toggleSubtask(subtaskId);
      loadTask();
    } catch (e) {
      console.error(e);
    }
  };

  const handlePostComment = async () => {
    if (!commentText.trim()) return;
    try {
      await taskService.addComment(taskId, commentText.trim());
      setCommentText("");
      loadTask();
    } catch (e) {
      console.error(e);
    }
  };

  const handleStatusChange = async (status: string) => {
    try {
      await taskService.updateTaskStatus(taskId, status);
      loadTask();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading || !task) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#4f46e5" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>{task.title}</Text>
        <Text style={styles.desc}>{task.description || "No description provided"}</Text>

        {/* Status Switcher */}
        <Text style={styles.label}>Update Status:</Text>
        <View style={styles.statusRow}>
          {["todo", "in_progress", "in_review", "completed"].map((st) => (
            <TouchableOpacity
              key={st}
              style={[
                styles.statusBtn,
                task.status === st && styles.statusBtnActive,
              ]}
              onPress={() => handleStatusChange(st)}
            >
              <Text
                style={[
                  styles.statusBtnText,
                  task.status === st && styles.statusBtnTextActive,
                ]}
              >
                {st.replace("_", " ")}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Subtasks */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>
          Subtasks ({task.subtasks?.filter((s) => s.is_completed).length || 0}/
          {task.subtasks?.length || 0})
        </Text>
        {task.subtasks?.map((sub) => (
          <TouchableOpacity
            key={sub.id}
            style={styles.subtaskItem}
            onPress={() => handleToggleSubtask(sub.id)}
          >
            <Text style={styles.checkboxIcon}>{sub.is_completed ? "☑" : "☐"}</Text>
            <Text
              style={[
                styles.subtaskTitle,
                sub.is_completed && styles.subtaskDone,
              ]}
            >
              {sub.title}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Discussion */}
      <View style={styles.card}>
        <Text style={styles.sectionTitle}>Discussion & Comments</Text>
        {comments.map((comm) => (
          <View key={comm.id} style={styles.commentItem}>
            <Text style={styles.commentAuthor}>{comm.author?.full_name || "Team Member"}</Text>
            <Text style={styles.commentContent}>{comm.content}</Text>
          </View>
        ))}

        <View style={styles.commentInputRow}>
          <TextInput
            style={styles.commentInput}
            placeholder="Write a comment..."
            value={commentText}
            onChangeText={setCommentText}
          />
          <TouchableOpacity style={styles.sendBtn} onPress={handlePostComment}>
            <Text style={styles.sendText}>Send</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc", padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    marginBottom: 12,
  },
  title: { fontSize: 16, fontWeight: "700", color: "#0f172a" },
  desc: { fontSize: 13, color: "#64748b", marginVertical: 8, lineHeight: 18 },
  label: { fontSize: 11, fontWeight: "700", color: "#94a3b8", textTransform: "uppercase", marginTop: 8 },
  statusRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 6 },
  statusBtn: {
    paddingHorizontal: 8,
    paddingVertical: 5,
    borderRadius: 6,
    backgroundColor: "#f1f5f9",
  },
  statusBtnActive: { backgroundColor: "#4f46e5" },
  statusBtnText: { fontSize: 11, fontWeight: "600", color: "#475569", textTransform: "capitalize" },
  statusBtnTextActive: { color: "#fff" },
  sectionTitle: { fontSize: 13, fontWeight: "700", color: "#0f172a", marginBottom: 8 },
  subtaskItem: { flexDirection: "row", alignItems: "center", paddingVertical: 6 },
  checkboxIcon: { fontSize: 16, marginRight: 8, color: "#4f46e5" },
  subtaskTitle: { fontSize: 13, color: "#334155" },
  subtaskDone: { textDecorationLine: "line-through", color: "#94a3b8" },
  commentItem: { paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: "#f1f5f9" },
  commentAuthor: { fontSize: 11, fontWeight: "700", color: "#0f172a" },
  commentContent: { fontSize: 12, color: "#475569", marginTop: 2 },
  commentInputRow: { flexDirection: "row", gap: 8, marginTop: 10 },
  commentInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#cbd5e1",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 12,
  },
  sendBtn: {
    backgroundColor: "#4f46e5",
    paddingHorizontal: 14,
    borderRadius: 8,
    justifyContent: "center",
  },
  sendText: { color: "#fff", fontWeight: "700", fontSize: 12 },
});
