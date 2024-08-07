import { NextResponse } from "next/server";

let wateringInfo = {
  duration: 10,
  delay: 14,
  time_remaining: 1209600, // 14 days in seconds
};

export async function GET() {
  return NextResponse.json(wateringInfo);
}

export async function POST(request) {
  const { duration, delay } = await request.json();
  wateringInfo = {
    duration: duration || wateringInfo.duration,
    delay: delay || wateringInfo.delay,
    time_remaining: delay * 86400, // Convert days to seconds
  };
  return NextResponse.json(wateringInfo);
}
