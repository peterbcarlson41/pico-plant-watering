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

  const handleNumericInput = (value, setValue) => {
    const newValue = value.replace(/[^0-9]/g, "").slice(0, 2); // Allow only numbers, limit to 2 digits
    setValue(newValue);
  };

  const handleSave = (e) => {
    e.preventDefault();

    // Check each input and set to "00" if empty
    const hrs = wateringTimeHours || "00";
    const mins = wateringTimeMinutes || "00";
    const secs = wateringTimeSeconds || "00";
    const durHrs = wateringDurationHours || "00";
    const durMins = wateringDurationMinutes || "00";
    const durSecs = wateringDurationSeconds || "00";

    // Format the time and duration for display
    const time = `${hrs}:${mins}:${secs}`;
    const duration = `${durHrs}:${durMins}:${durSecs}`;

    setDisplayedWateringTime(time);
    setDisplayedWateringDuration(duration);

    // Optionally reset fields here if needed
    // Resetting to empty strings; you might consider resetting to "00" instead
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
      <form
        onSubmit={handleSave}
        className="flex flex-col gap-5 w-full items-center"
      >
        <div className="flex flex-row w-full p-6 items-center gap-4">
          <div className="w-full">
            <Label htmlFor="time-display">Time between watering</Label>
            <Input
              id="time-display"
              readOnly
              value={displayedWateringTime || "Not set"}
            />
          </div>
          <div className="w-full">
            <Label htmlFor="duration-display">Watering duration</Label>
            <Input
              id="duration-display"
              readOnly
              value={displayedWateringDuration || "Not set"}
            />
          </div>
        </div>
        <div className="flex flex-col rounded-lg border sm:w-1/2 w-full border-gray-200 p-6 gap-2">
          <div className="flex flex-row gap-2">
            <div className="flex flex-col gap-2">
              <Label>Time between watering</Label>
              <div className="flex items-center border rounded-md">
                <Input
                  placeholder="00"
                  value={wateringTimeHours}
                  onChange={(e) =>
                    handleNumericInput(e.target.value, setWateringTimeHours)
                  }
                />
                <div className="font-bold px-1">:</div>
                <Input
                  placeholder="00"
                  value={wateringTimeMinutes}
                  onChange={(e) =>
                    handleNumericInput(e.target.value, setWateringTimeMinutes)
                  }
                />
                <div className="font-bold px-1">:</div>
                <Input
                  placeholder="00"
                  value={wateringTimeSeconds}
                  onChange={(e) =>
                    handleNumericInput(e.target.value, setWateringTimeSeconds)
                  }
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label>Watering duration</Label>
              <div className="flex items-center border rounded-md">
                <Input
                  placeholder="00"
                  value={wateringDurationHours}
                  onChange={(e) =>
                    handleNumericInput(e.target.value, setWateringDurationHours)
                  }
                />
                <div className="font-bold px-1">:</div>
                <Input
                  placeholder="00"
                  value={wateringDurationMinutes}
                  onChange={(e) =>
                    handleNumericInput(
                      e.target.value,
                      setWateringDurationMinutes
                    )
                  }
                />
                <div className="font-bold px-1">:</div>
                <Input
                  placeholder="00"
                  value={wateringDurationSeconds}
                  onChange={(e) =>
                    handleNumericInput(
                      e.target.value,
                      setWateringDurationSeconds
                    )
                  }
                />
              </div>
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
