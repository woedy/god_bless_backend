import React, { useState, useEffect } from "react";

function TaskProgress({ taskId }) {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState("Task is starting...");

  useEffect(() => {
    const socket = new WebSocket(`ws://localhost:8000/ws/task_progress/${taskId}/`);

    socket.onopen = () => {
      console.log("WebSocket connection established");
    };

    socket.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setStatus(data.state);

      if (data.progress !== undefined) {
        setProgress(data.progress);
      }

      if (data.result) {
        setStatus("Task completed successfully!");
      }

      if (data.error) {
        setStatus(`Task failed: ${data.error}`);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket connection closed");
    };

    return () => socket.close(); // Cleanup on component unmount
  }, [taskId]);

  return (
    <div>
      <h3>Status: {status}</h3>
      {status === "PROGRESS" && (
        <div>
          <p>Progress: {Math.round(progress)}%</p>
          <progress value={progress} max="100" />
        </div>
      )}
    </div>
  );
}

export default TaskProgress;
