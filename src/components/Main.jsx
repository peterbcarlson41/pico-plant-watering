"use client";

import { useState } from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Main() {
  const [wateringTime, setWateringTime] = useState("");
  const [wateringDuration, setWateringDuration] = useState("");
  const [displayedWateringTime, setDisplayedWateringTime] = useState("");
  const [displayedWateringDuration, setDisplayedWateringDuration] =
    useState("");

  const handleSave = (e) => {
    e.preventDefault();

    setDisplayedWateringTime(wateringTime);
    setDisplayedWateringDuration(wateringDuration);

    setWateringTime("");
    setWateringDuration("");
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
        <div className="rounded-lg border border-gray-200 grid w-full p-6 items-center gap-4">
          <div className="grid gap-2">
            <Label htmlFor="time">Time between watering</Label>
            <Input
              id="time"
              placeholder="dd:mm:ss"
              value={wateringTime}
              onChange={(e) => setWateringTime(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="duration">Watering duration</Label>
            <Input
              id="duration"
              placeholder="mm:ss"
              value={wateringDuration}
              onChange={(e) => setWateringDuration(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full">
            Save
          </Button>
        </div>
      </form>
    </main>
  );
}
