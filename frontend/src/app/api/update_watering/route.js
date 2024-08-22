import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

const WATERING_TIME_FILE = path.join(process.cwd(), "watering_time.txt");
const WATERING_INFO_FILE = path.join(process.cwd(), "watering_info.json");

async function saveWateringTime(timestamp) {
  try {
    await fs.writeFile(WATERING_TIME_FILE, timestamp.toString());
  } catch (error) {
    console.error("Error writing watering time file:", error);
  }
}

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

async function saveWateringInfo(info) {
  try {
    await fs.writeFile(WATERING_INFO_FILE, JSON.stringify(info));
  } catch (error) {
    console.error("Error writing watering info file:", error);
  }
}

export async function POST(request) {
  const { duration, delay } = await request.json();
  let currentInfo = await loadWateringInfo();

  if (duration !== undefined) {
    currentInfo.duration = duration;
  }

  if (delay !== undefined) {
    currentInfo.delay = delay;
    const nextWateringTime = Date.now() + delay * 86400000; // Convert days to milliseconds
    await saveWateringTime(nextWateringTime);
  }

  await saveWateringInfo(currentInfo);

  // Calculate time_remaining
  const savedWateringTime = await loadWateringTime();
  if (savedWateringTime) {
    const currentTime = Date.now();
    currentInfo.time_remaining = Math.max(
      0,
      Math.floor((savedWateringTime - currentTime) / 1000)
    );
  } else {
    currentInfo.time_remaining = currentInfo.delay * 86400; // Convert days to seconds
  }

  return NextResponse.json(currentInfo);
}
