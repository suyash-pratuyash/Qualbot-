import { useState } from "react";
import ChatWidget from "./ChatWidget";
import Dashboard from "./Dashboard";

export default function App() {
  const [page, setPage] = useState("chat");
  const [adminKey, setAdminKey] = useState(
    () => sessionStorage.getItem("qualbot-admin-key") || "",
  );

  function updateAdminKey(value) {
    setAdminKey(value);
    if (value) sessionStorage.setItem("qualbot-admin-key", value);
    else sessionStorage.removeItem("qualbot-admin-key");
  }

  return (
    <main className="min-h-screen px-4 py-6 sm:px-8 sm:py-10">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] text-indigo-600">
              Conversational lead qualification
            </p>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              QualBot
            </h1>
            <p className="mt-2 max-w-xl text-sm text-slate-500">
              Qualify prospects naturally, then keep every conversation and
              lead score in one place.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:items-end">
            <label className="text-xs text-slate-500">
              Admin API key
              <input
                className="text-input mt-1 w-full sm:w-64"
                type="password"
                autoComplete="off"
                value={adminKey}
                onChange={(event) => updateAdminKey(event.target.value)}
                placeholder="Required to view saved leads"
              />
            </label>
            <nav className="flex w-fit rounded-xl border border-slate-200 bg-white p-1 shadow-sm">
              <button
                className={`nav-button ${page === "chat" ? "nav-button-active" : ""}`}
                onClick={() => setPage("chat")}
              >
                Chat
              </button>
              <button
                className={`nav-button ${page === "dashboard" ? "nav-button-active" : ""}`}
                onClick={() => setPage("dashboard")}
              >
                Lead dashboard
              </button>
            </nav>
          </div>
        </header>

        {page === "chat" ? (
          <ChatWidget adminKey={adminKey} />
        ) : (
          <Dashboard adminKey={adminKey} />
        )}
      </div>
    </main>
  );
}
