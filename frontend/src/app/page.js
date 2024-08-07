"use client";
import { useState, useEffect } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const PICO_IP = "192.168.1.170:8080"; // Replace with your Pico's IP address

const API_URL = process.env.NEXT_PUBLIC_USE_MOCK_API
  ? "/api/"
  : `http://${PICO_IP}`;

export default function Component() {
  const [duration, setDuration] = useState("");
  const [delay, setDelay] = useState("");
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    checkBackendStatus();
    fetchWateringInfo();
    const interval = setInterval(() => {
      checkBackendStatus();
      fetchWateringInfo();
    }, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining((prevTime) => Math.max(0, prevTime - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/watering_info`);
      setBackendStatus(response.ok ? "Online" : "Offline");
    } catch (err) {
      setBackendStatus("Offline");
    }
  };

  const fetchWateringInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/watering_info`);
      const data = await response.json();
      updateStateWithWateringInfo(data);
    } catch (err) {
      console.error("Error fetching watering info:", err);
    }
  };

  const formatTimeRemaining = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    return `${days}:${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  const startMotor = async () => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/start_motor`, {
        method: "POST",
      });
      if (!response.ok) throw new Error("Failed to start motor");
      const data = await response.json();
    } catch (err) {
      console.error("Error starting motor:", err);
      setError("Failed to start motor. Please try again.");
    }
  };

  const updateStateWithWateringInfo = (data) => {
    setDuration(data.duration.toString());
    setDelay(data.delay.toString());
    setTimeRemaining(data.time_remaining);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/update_watering`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          duration: Number(duration),
          delay: Number(delay),
        }),
      });

      if (!response.ok) throw new Error("Failed to update watering settings");

      const data = await response.json();
      updateStateWithWateringInfo(data);
    } catch (err) {
      console.error("Error updating watering settings:", err);
      setError("Failed to update watering settings. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
      <div className="max-w-md w-full space-y-6 p-6 rounded-lg sm:shadow-lg sm:bg-card">
        <div className="text-center">
          <Badge
            variant="outline"
            className={
              backendStatus === "Online" ? "text-green-500" : "text-red-500"
            }
          >
            {backendStatus}
          </Badge>
          <h1 className="text-3xl font-bold">Plant Watering System</h1>
          <p className="text-muted-foreground">
            Control your plant's watering schedule
          </p>
        </div>
        {error && <div className="text-red-500 text-center">{error}</div>}
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <Label htmlFor="duration">Watering Duration (seconds)</Label>
            <Input
              id="duration"
              type="number"
              min="1"
              max="30"
              placeholder="Enter duration in seconds"
              className="mt-1"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
            />
          </div>
          <div>
            <Label htmlFor="delay">Delay Between Waterings (days)</Label>
            <Input
              id="delay"
              type="number"
              min="1"
              max="30"
              placeholder="Enter delay in days"
              className="mt-1"
              value={delay}
              onChange={(e) => setDelay(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Updating..." : "Update Watering Settings"}
          </Button>
        </form>
        <div className="bg-muted p-4 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Next Watering In:</span>
            <span className="text-2xl font-bold">
              {formatTimeRemaining(timeRemaining)}
            </span>
          </div>
        </div>
        <div className="flex justify-between space-x-2">
          <Button onClick={startMotor}>Test Motor</Button>
          <Button onClick={fetchWateringInfo}>Refresh Watering Time</Button>
        </div>
      </div>
    </div>
  );
}
