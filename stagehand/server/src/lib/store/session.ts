import { type SessionCreateResponse } from "@browserbasehq/sdk/src/resources/index.js";
import { create } from "zustand";
import { devtools, persist } from "zustand/middleware";

interface SessionState {
  session: SessionCreateResponse | null;
  setSession: (session: SessionCreateResponse | null) => void;
  browserbaseApiKey: string | null;
  setBrowserbaseApiKey: (apiKey: string | null) => void;
  browserbaseProjectId: string | null;
  setBrowserbaseProjectId: (projectId: string | null) => void;
  openaiApiKey: string | null;
  setOpenaiApiKey: (apiKey: string | null) => void;
}

export const useSessionStore = create<SessionState>()(
  devtools(
    persist(
      (set) => ({
        session: null,
        setSession: (session) => set({ session }),
        browserbaseApiKey: null,
        setBrowserbaseApiKey: (apiKey) => set({ browserbaseApiKey: apiKey }),
        browserbaseProjectId: null,
        setBrowserbaseProjectId: (projectId) =>
          set({ browserbaseProjectId: projectId }),
        openaiApiKey: null,
        setOpenaiApiKey: (apiKey) => set({ openaiApiKey: apiKey }),
      }),
      {
        name: "session-storage",
      }
    )
  )
);
