import StreamViewer from "@/components/client/streamViewer";

export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-2xl font-bold mb-4 text-center">
        Next.js Streaming Demo
      </h1>
      <StreamViewer />
    </main>
  );
}
