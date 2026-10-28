import { useEffect, useRef, useState } from "react";
import { requestApi } from "./api";

/**
 * Helper to pick color styles based on lead tier
 * Used for visual feedback: Hot (red/rose), Warm (amber), Cold (sky/blue)
 */
function getTierBadgeClass(tier) {
  if (tier === "hot") return "bg-rose-100 text-rose-700 border border-rose-200";
  if (tier === "warm") return "bg-amber-100 text-amber-700 border border-amber-200";
  return "bg-sky-100 text-sky-700 border border-sky-200";
}

/**
 * Helper to style BANT criteria values (e.g. "confirmed" vs "unknown")
 */
function getBantValueClass(value) {
  if (!value || value === "unknown") return "text-slate-400 bg-slate-100";
  if (value === "confirmed" || value === "decision_maker" || value === "clear" || value === "immediate") {
    return "text-emerald-700 bg-emerald-50 border border-emerald-200";
  }
  return "text-amber-700 bg-amber-50 border border-amber-200";
}

export default function ChatWidget() {
  // -------------------------------------------------------------
  // 1. STATE MANAGEMENT
  // -------------------------------------------------------------

  // Session ID: identifies the conversation session in backend SQLite
  const [sessionId, setSessionId] = useState(() => {
    return localStorage.getItem("qualbot-session-id") || `lead-${Date.now()}`;
  });

  // Conversation messages: array of { role: "user" | "assistant", content: string }
  const [messages, setMessages] = useState([]);

  // Current text in the input box
  const [input, setInput] = useState("");

  // Loading state while backend/Gemini generates response
  const [loading, setLoading] = useState(false);

  // Qualification data: score, tier, BANT fields, and next action (e.g. Calendly link)
  const [leadInfo, setLeadInfo] = useState({
    score: null,
    tier: "cold",
    bant: { budget: "unknown", authority: "unknown", need: "unknown", timeline: "unknown" },
    action: null,
  });

  // Error message state
  const [error, setError] = useState("");

  // Ref to automatically scroll chat to bottom when new messages arrive
  const chatBottomRef = useRef(null);

  // -------------------------------------------------------------
  // 2. LIFECYCLE (LOAD EXISTING CHAT ON MOUNT / SESSION CHANGE)
  // -------------------------------------------------------------
  useEffect(() => {
    async function loadChat() {
      setError("");
      try {
        // Fetch existing lead transcript if available
        const lead = await requestApi(`/leads/${encodeURIComponent(sessionId)}`);
        if (lead) {
          setMessages(lead.transcript.map((m) => ({ role: m.role, content: m.content })));
          setLeadInfo({
            score: lead.score,
            tier: lead.tier,
            bant: lead.bant,
            action: lead.action,
          });
        }
      } catch (err) {
        // 404 is normal for a brand new session with no messages yet
        if (err.status !== 404) {
          setError("Could not load previous conversation history.");
        }
      }
    }

    loadChat();
  }, [sessionId]);

  // Auto-scroll whenever messages change or loading state toggles
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // -------------------------------------------------------------
  // 3. ACTION HANDLERS
  // -------------------------------------------------------------

  // Send a prospect message to the FastAPI backend (/chat)
  async function handleSendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    // Instantly append user's message to UI for smooth experience
    const newHistory = [...messages, { role: "user", content: text }];
    setMessages(newHistory);
    setInput("");
    setLoading(true);
    setError("");

    try {
      // POST message to backend
      const data = await requestApi("/chat", {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          message: text,
        }),
      });

      // Append assistant's reply
      setMessages([...newHistory, { role: "assistant", content: data.reply }]);

      // Update qualification score, tier, and BANT extracted by backend
      setLeadInfo({
        score: data.score,
        tier: data.tier,
        bant: data.bant,
        action: data.action,
      });
    } catch (err) {
      setError(err.message || "Failed to send message. Please ensure the backend is running.");
      // Rollback the optimistic user message if call failed
      setMessages(messages);
      setInput(text);
    } finally {
      setLoading(false);
    }
  }

  // Reset the conversation and start a new lead session
  function handleNewChat() {
    const newId = `lead-${Date.now()}`;
    localStorage.setItem("qualbot-session-id", newId);
    setSessionId(newId);
    setMessages([]);
    setLeadInfo({
      score: null,
      tier: "cold",
      bant: { budget: "unknown", authority: "unknown", need: "unknown", timeline: "unknown" },
      action: null,
    });
    setError("");
  }

  // -------------------------------------------------------------
  // 4. UI RENDER
  // -------------------------------------------------------------
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
      {/* LEFT 2 COLUMNS: CHAT WINDOW */}
      <div className="lg:col-span-2 flex flex-col h-[650px] bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {/* Chat Header */}
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4 bg-slate-50/50">
          <div>
            <h2 className="text-base font-semibold text-slate-800">Prospect Chat</h2>
            <p className="text-xs text-slate-500 font-mono mt-0.5">Session: {sessionId}</p>
          </div>
          <button
            onClick={handleNewChat}
            className="px-3.5 py-1.5 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-lg hover:border-indigo-300 hover:text-indigo-600 transition shadow-xs"
          >
            + New Chat
          </button>
        </div>

        {/* Chat Message Thread */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/40">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center max-w-sm mx-auto">
              <div className="w-12 h-12 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-lg mb-3">
                Q
              </div>
              <h3 className="text-sm font-semibold text-slate-800">Start a Qualification Chat</h3>
              <p className="text-xs text-slate-500 mt-1">
                Say hello or describe your product/budget requirements. QualBot will extract BANT metrics in real time.
              </p>
            </div>
          )}

          {messages.map((msg, index) => {
            const isUser = msg.role === "user";
            return (
              <div key={index} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    isUser
                      ? "bg-indigo-600 text-white rounded-br-xs shadow-xs"
                      : "bg-white text-slate-800 border border-slate-200 rounded-bl-xs shadow-xs"
                  }`}
                >
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            );
          })}

          {/* Typing indicator */}
          {loading && (
            <div className="flex items-center gap-2 text-xs text-slate-400 italic py-1">
              <span className="inline-block w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
              QualBot is analyzing and responding…
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Error notification if any */}
        {error && (
          <div className="px-6 py-2 bg-rose-50 border-t border-rose-100 text-xs text-rose-600 font-medium">
            {error}
          </div>
        )}

        {/* Message Input Form */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-slate-100 bg-white flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your reply (e.g., We have a $5000 budget and need this next month)..."
            disabled={loading}
            className="flex-1 rounded-xl border border-slate-200 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 transition"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-xs"
          >
            Send
          </button>
        </form>
      </div>

      {/* RIGHT 1 COLUMN: LIVE QUALIFICATION & LEAD SCORE */}
      <div className="space-y-6">
        {/* Score Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-semibold text-slate-900">Lead Score</h3>
              <p className="text-xs text-slate-500 mt-0.5">Calculated from BANT metrics</p>
            </div>
            <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase tracking-wide ${getTierBadgeClass(leadInfo.tier)}`}>
              {leadInfo.tier}
            </span>
          </div>

          <div className="mt-5 flex items-baseline gap-2">
            <span className="text-5xl font-black tracking-tight text-slate-900">
              {leadInfo.score !== null ? leadInfo.score : "—"}
            </span>
            <span className="text-sm font-medium text-slate-400">/ 100</span>
          </div>

          {/* Action Button: shows if warm/hot with Calendly link */}
          {leadInfo.action?.url && (
            <a
              href={leadInfo.action.url}
              target="_blank"
              rel="noreferrer"
              className="mt-5 block w-full py-2.5 text-center text-sm font-semibold text-white bg-emerald-600 rounded-xl hover:bg-emerald-700 transition shadow-xs"
            >
              📅 Schedule Meeting
            </a>
          )}
        </div>

        {/* BANT Metrics Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-900">BANT Qualification</h3>
          <p className="text-xs text-slate-500 mt-0.5">Extracted automatically from chat</p>

          <div className="mt-4 space-y-3">
            {[
              { label: "Budget", key: "budget", desc: "Financial capacity" },
              { label: "Authority", key: "authority", desc: "Decision maker" },
              { label: "Need", key: "need", desc: "Business fit" },
              { label: "Timeline", key: "timeline", desc: "Purchase urgency" },
            ].map(({ label, key, desc }) => {
              const val = leadInfo.bant?.[key] || "unknown";
              return (
                <div key={key} className="flex items-center justify-between p-2.5 rounded-xl border border-slate-100 bg-slate-50/60">
                  <div>
                    <p className="text-xs font-semibold text-slate-700">{label}</p>
                    <p className="text-[11px] text-slate-400">{desc}</p>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-md text-xs font-medium capitalize ${getBantValueClass(val)}`}>
                    {val.replace("_", " ")}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
