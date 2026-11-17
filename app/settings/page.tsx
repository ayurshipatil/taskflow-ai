"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { apiRequest } from "@/lib/api";
import { Settings as SettingsIcon, Shield, User, Building, CheckCircle2 } from "lucide-react";

export default function SettingsPage() {
  const router = useRouter();
  const { user, activeWorkspace, refreshUser } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || "");
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || "");
  const [newPassword, setNewPassword] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);
  const [message, setMessage] = useState("");

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    setMessage("");
    try {
      await apiRequest("/auth/profile", {
        method: "PUT",
        body: JSON.stringify({
          full_name: fullName.trim(),
          avatar_url: avatarUrl.trim() || null,
          password: newPassword ? newPassword : null,
        }),
      });
      await refreshUser();
      setNewPassword("");
      setMessage("Profile settings successfully updated!");
    } catch (e: any) {
      setMessage(e.message || "Failed to update profile");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950">
      <Sidebar />

      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />

        <main className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl">
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <SettingsIcon className="w-5 h-5 text-indigo-600" />
              <span>Account & Workspace Settings</span>
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Update personal identity credentials and manage organization permissions
            </p>
          </div>

          {message && (
            <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-xs text-indigo-700 dark:text-indigo-300 font-semibold flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-indigo-500" />
              <span>{message}</span>
            </div>
          )}

          {/* User Profile Form */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <User className="w-4 h-4 text-indigo-500" />
              <span>User Profile Details</span>
            </h3>

            <form onSubmit={handleUpdateProfile} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-white focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                    Email (Read-only)
                  </label>
                  <input
                    type="email"
                    disabled
                    value={user?.email || ""}
                    className="w-full bg-slate-100 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-500 dark:text-slate-400 cursor-not-allowed"
                  />
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Avatar Image URL
                </label>
                <input
                  type="url"
                  placeholder="https://example.com/photo.jpg"
                  value={avatarUrl}
                  onChange={(e) => setAvatarUrl(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-white focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="font-semibold text-slate-700 dark:text-slate-300 block mb-1">
                  Change Password (Leave blank to keep existing)
                </label>
                <input
                  type="password"
                  placeholder="New secure password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-xs text-slate-900 dark:text-white focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isUpdating}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg text-xs transition disabled:opacity-50"
                >
                  {isUpdating ? "Saving..." : "Save Profile"}
                </button>
              </div>
            </form>
          </div>

          {/* Active Workspace Info */}
          <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-3">
            <h3 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider flex items-center gap-2">
              <Building className="w-4 h-4 text-indigo-500" />
              <span>Active Workspace</span>
            </h3>

            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200/60 dark:border-slate-700 text-xs space-y-1">
              <p className="font-bold text-slate-900 dark:text-white">
                {activeWorkspace?.name || "Acme Enterprise"}
              </p>
              <p className="text-slate-500 dark:text-slate-400">
                Slug identifier: <code className="font-mono text-indigo-600 dark:text-indigo-400">{activeWorkspace?.slug}</code>
              </p>
              <p className="text-slate-500 dark:text-slate-400">
                Your Global Role: <strong className="capitalize text-slate-800 dark:text-slate-200">{user?.role?.replace("_", " ")}</strong>
              </p>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
