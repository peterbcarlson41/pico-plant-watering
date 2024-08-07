import { NextResponse } from "next/server";

export async function POST(request) {
  const motorRun = { status: "motor running" };
  return NextResponse.json(motorRun);
}
