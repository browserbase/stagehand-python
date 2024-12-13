import { NextResponse } from "next/server";

export async function GET() {
  return new NextResponse(
    JSON.stringify({
      status: "healthy",
      timestamp: new Date().toISOString(),
      version: process.env.VERSION || "development"
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
      }
    }
  );
} 