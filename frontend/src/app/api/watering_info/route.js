import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const WATERING_TIME_FILE = path.join(process.cwd(), "watering_time.txt");
const WATERING_INFO_FILE = path.join(process.cwd(), "watering_info.json");

async function loadWateringTime() {
  try {
    const data = await fs.readFile(WATERING_TIME_FILE, "utf8");
    return parseInt(data.trim(), 10);
  } catch (error) {
    if (error.code !== "ENOENT") {
      console.error("Error reading watering time file:", error);
    }
    return null;
  }
}

async function loadWateringInfo() {
  try {
    const data = await fs.readFile(WATERING_INFO_FILE, "utf8");
    return JSON.parse(data);
  } catch (error) {
    if (error.code !== "ENOENT") {
      console.error("Error reading watering info file:", error);
    }
    return { duration: 10, delay: 14 }; // Default values
  }
}

async function updateTimeRemaining(wateringInfo) {
  const savedTime = await loadWateringTime();
  const currentTime = Date.now();
  if (savedTime) {
    wateringInfo.time_remaining = Math.max(
      0,
      Math.floor((savedTime - currentTime) / 1000)
    );
  } else {
    // If no saved time, set time_remaining to the default delay
    wateringInfo.time_remaining = wateringInfo.delay * 86400;
  }
}

export async function GET() {
  let wateringInfo = await loadWateringInfo();
  await updateTimeRemaining(wateringInfo);
  return NextResponse.json(wateringInfo);
}
