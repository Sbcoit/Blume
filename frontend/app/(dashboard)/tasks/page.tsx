"use client";

import React, { useState, useEffect } from "react";
import { TaskCard, Task } from "@/components/TaskCard";
import { TaskModal } from "@/components/TaskModal";
import { api } from "@/lib/api";

type TaskStatus = "pending" | "completed" | "failed" | "all";
type TaskType = "scheduling" | "research" | "document" | "workflow" | "call" | "text" | "all";

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "all">("all");
  const [typeFilter, setTypeFilter] = useState<TaskType>("all");
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    filterTasks();
  }, [tasks, searchQuery, statusFilter, typeFilter]);

  const fetchTasks = async () => {
    try {
      // const response = await api.get<Task[]>("/api/v1/tasks");
      // setTasks(response);
      
      // Mock data for demo
      setTasks([]);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterTasks = () => {
    let filtered = [...tasks];

    if (searchQuery) {
      filtered = filtered.filter((task) =>
        task.input.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== "all") {
      filtered = filtered.filter((task) => task.status === statusFilter);
    }

    if (typeFilter !== "all") {
      filtered = filtered.filter((task) => task.type === typeFilter);
    }

    setFilteredTasks(filtered);
  };

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setIsModalOpen(true);
  };

  const selectedTaskIndex = selectedTask
    ? filteredTasks.findIndex((t) => t.id === selectedTask.id)
    : -1;

  const handleNext = () => {
    if (selectedTaskIndex < filteredTasks.length - 1) {
      setSelectedTask(filteredTasks[selectedTaskIndex + 1]);
    }
  };

  const handlePrevious = () => {
    if (selectedTaskIndex > 0) {
      setSelectedTask(filteredTasks[selectedTaskIndex - 1]);
    }
  };

  if (isLoading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "60vh" }}>
        <div className="body-base" style={{ color: "var(--text-secondary)" }}>Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Single Card with Filters and Content */}
      <div className="glass-card" style={{ padding: "1.5rem", paddingTop: "1rem", minHeight: "80vh" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          {/* Search */}
          <div style={{ flex: "1 1 250px", minWidth: "200px" }}>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: "100%" }}
            />
          </div>

          {/* Status Filter */}
          <div style={{ flex: "0 1 150px", minWidth: "120px" }}>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as TaskStatus | "all")}
              style={{ width: "100%" }}
            >
              <option value="all">All Status</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          {/* Type Filter */}
          <div style={{ flex: "0 1 150px", minWidth: "120px" }}>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value as TaskType)}
              style={{ width: "100%" }}
            >
              <option value="all">All Types</option>
              <option value="scheduling">Scheduling</option>
              <option value="research">Research</option>
              <option value="document">Document</option>
              <option value="workflow">Workflow</option>
              <option value="call">Call</option>
              <option value="text">Text</option>
            </select>
          </div>
        </div>

        {/* Task Grid or Empty State */}
        {filteredTasks.length === 0 ? (
          <div style={{ textAlign: "center", padding: "3rem 2rem" }}>
            <p className="body-base" style={{ color: "var(--text-secondary)" }}>
              {searchQuery ? "No tasks match your search" : "No tasks yet"}
            </p>
          </div>
        ) : (
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            gap: "1.5rem"
          }}>
            {filteredTasks.map((task, index) => (
              <div
                key={task.id}
                className="stagger-animate"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <TaskCard task={task} onClick={() => handleTaskClick(task)} />
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Task Modal */}
      <TaskModal
        task={selectedTask}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onNext={handleNext}
        onPrevious={handlePrevious}
        hasNext={selectedTaskIndex < filteredTasks.length - 1}
        hasPrevious={selectedTaskIndex > 0}
      />
    </div>
  );
}
