"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Main() {
  // State for watering time
  const [wateringTimeHours, setWateringTimeHours] = useState("");
  const [wateringTimeMinutes, setWateringTimeMinutes] = useState("");
  const [wateringTimeSeconds, setWateringTimeSeconds] = useState("");

  // State for watering duration
  const [wateringDurationHours, setWateringDurationHours] = useState("");
  const [wateringDurationMinutes, setWateringDurationMinutes] = useState("");
  const [wateringDurationSeconds, setWateringDurationSeconds] = useState("");

  // State for displaying watering time and duration
  const [displayedWateringTime, setDisplayedWateringTime] = useState("");
  const [displayedWateringDuration, setDisplayedWateringDuration] =
    useState("");

  const handleSave = (e) => {
    e.preventDefault();

    // Format the time and duration for display
    const time = `${wateringTimeHours}:${wateringTimeMinutes}:${wateringTimeSeconds}`;
    const duration = `${wateringDurationHours}:${wateringDurationMinutes}:${wateringDurationSeconds}`;

    setDisplayedWateringTime(time);
    setDisplayedWateringDuration(duration);

    // Reset fields
    setWateringTimeHours("");
    setWateringTimeMinutes("");
    setWateringTimeSeconds("");
    setWateringDurationHours("");
    setWateringDurationMinutes("");
    setWateringDurationSeconds("");
  };

  return (
    <main className="flex flex-col px-4 sm:px-6 lg:px-8 w-full min-h-screen">
      <div className="space-y-2 py-5">
        <h1 className="text-3xl font-bold">Watering Schedule</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Specify the time interval between watering and the duration of each
          watering session.
        </p>
      </div>
      <form onSubmit={handleSave} className="flex flex-col gap-5 w-full">
        <div className="flex flex-row w-full p-6 items-center gap-4">
          <div className="w-full">
            <Label htmlFor="time-display">Time between watering</Label>
            <Input
              id="time-display"
              className="border-none"
              readOnly
              value={displayedWateringTime || "Not set"}
            />
          </div>
          <div className="w-full">
            <Label htmlFor="duration-display">Watering duration</Label>
            <Input
              id="duration-display"
              className="border-none"
              readOnly
              value={displayedWateringDuration || "Not set"}
            />
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 grid grid-cols-3 gap-4 p-6">
          <div className="flex flex-col gap-2">
            <Label>Time between watering</Label>
            <div className="flex items-center border rounded-md">
              <Input
                placeholder="00"
                value={wateringTimeHours}
                onChange={(e) => setWateringTimeHours(e.target.value)}
              />
              <div className="font-bold px-1">:</div>
              <Input
                placeholder="00"
                value={wateringTimeMinutes}
                onChange={(e) => setWateringTimeMinutes(e.target.value)}
              />
              <div className="font-bold px-1">:</div>
              <Input
                placeholder="00"
                value={wateringTimeSeconds}
                onChange={(e) => setWateringTimeSeconds(e.target.value)}
              />
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <Label>Watering duration</Label>
            <div className="flex items-center border rounded-md">
              <Input
                placeholder="00"
                value={wateringDurationHours}
                onChange={(e) => setWateringDurationHours(e.target.value)}
              />
              <div className="font-bold px-1">:</div>
              <Input
                placeholder="00"
                value={wateringDurationMinutes}
                onChange={(e) => setWateringDurationMinutes(e.target.value)}
              />
              <div className="font-bold px-1">:</div>
              <Input
                placeholder="00"
                value={wateringDurationSeconds}
                onChange={(e) => setWateringDurationSeconds(e.target.value)}
              />
            </div>
          </div>
          <Button type="submit" className="col-span-3">
            Save
          </Button>
        </div>
      </form>
    </main>
  );
}
