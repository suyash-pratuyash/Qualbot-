import { useState } from "react";
import ChatWidget from "./ChatWidget";
import Dashboard from "./Dashboard";

/**
 * App Component
 * Root component that manages the top-level tab navigation ("chat" vs "dashboard")
 * and renders either ChatWidget (for prospects) or Dashboard (for sales team).
 */
export default function App() {
  // Navigation state: "chat" or "dashboard"
  const [activeTab, setActiveTab] = useState("chat");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 font-sans antialiased">
      {/* Top Navigation Bar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          {/* Logo and Subtitle */}
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-xs">
                Q
              </div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">
                QualBot
              </h1>
              <span className="text-[11px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-100">
                AI Lead Qualification
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Conversational BANT scoring powered by Google Gemini & FastAPI.
            </p>
          </div>

          {/* Tab Navigation Pill */}
          <nav className="flex items-center p-1 bg-slate-100 rounded-xl border border-slate-200 w-fit">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition ${
                activeTab === "chat"
                  ? "bg-white text-indigo-600 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              💬 Prospect Chat
            </button>
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition ${
                activeTab === "dashboard"
                  ? "bg-white text-indigo-600 shadow-xs"
                  : "text-slate-600 hover:text-slate-900"
              }`}
            >
              📊 Lead Dashboard
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {activeTab === "chat" ? <ChatWidget /> : <Dashboard />}
      </main>
    </div>
  );
}
