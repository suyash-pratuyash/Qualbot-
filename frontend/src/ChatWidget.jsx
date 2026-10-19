import { useEffect, useRef, useState } from "react";
import { requestApi } from "./api";

function newSessionId() {
  return `lead-${crypto.randomUUID()}`;
}

function tierClass(tier) {
  if (tier === "hot") return "tier-hot";
  if (tier === "warm") return "tier-warm";
  return "tier-cold";
}

export default function ChatWidget({ adminKey }) {
  const [sessionId, setSessionId] = useState(() => {
    const saved = localStorage.getItem("qualbot-session-id");
    if (saved) return saved;
    const id = newSessionId();
    localStorage.setItem("qualbot-session-id", id);
    return id;
  });
  const [messages, setMessages] = useState([]);
  const [bant, setBant] = useState(null);
  const [score, setScore] = useState(null);
  const [tier, setTier] = useState("cold");
  const [action, setAction] = useState(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);
  const activeSessionId = useRef(sessionId);

  useEffect(() => {
    let active = true;
    requestApi(`/leads/${encodeURIComponent(sessionId)}`, {
      headers: { "X-Admin-Key": adminKey },
    })
      .then((lead) => {
        if (!active) return;
        setMessages(
          lead.transcript.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        );
        setBant(lead.bant);
        setScore(lead.score);
        setTier(lead.tier);
        setAction(lead.action);
      })
      .catch((requestError) => {
        if (requestError.status !== 404 && active) {
          setError(`Could not load this chat: ${requestError.message}`);
        }
      });
    return () => {
      active = false;
    };
  }, [sessionId, adminKey]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function sendMessage(event) {
    event.preventDefault();
    const message = input.trim();
    if (!message || busy) return;
    const requestSessionId = sessionId;

    setInput("");
    setError("");
    setMessages((current) => [...current, { role: "user", content: message }]);
    setBusy(true);
    try {
      const result = await requestApi("/chat", {
        method: "POST",
        body: JSON.stringify({ session_id: requestSessionId, message }),
      });
      if (activeSessionId.current !== requestSessionId) return;
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.reply },
      ]);
      setBant(result.bant);
      setScore(result.score);
      setTier(result.tier);
      setAction(result.action);
    } catch (requestError) {
      if (activeSessionId.current !== requestSessionId) return;
      setError(requestError.message);
      setMessages((current) => current.slice(0, -1));
      setInput(message);
    } finally {
      setBusy(false);
    }
  }

  function startNewChat() {
    const id = newSessionId();
    activeSessionId.current = id;
    localStorage.setItem("qualbot-session-id", id);
    setSessionId(id);
    setMessages([]);
    setBant(null);
    setScore(null);
    setTier("cold");
    setAction(null);
    setError("");
  }

  return (
    <section className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px]">
      <div className="panel flex min-h-[620px] flex-col overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <div>
            <h2 className="font-semibold text-slate-900">Prospect chat</h2>
            <p className="mt-1 text-xs text-slate-500">
              Session: <span className="font-mono">{sessionId.slice(0, 18)}…</span>
            </p>
          </div>
          <button className="secondary-button" onClick={startNewChat}>
            New chat
          </button>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto bg-slate-50/70 p-5">
          {messages.length === 0 && (
            <div className="mx-auto mt-16 max-w-sm text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-100 text-xl text-indigo-700">
                Q
              </div>
              <h3 className="font-semibold text-slate-800">
                Start a qualification conversation
              </h3>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Ask about a business need, or introduce yourself as a
                prospective customer.
              </p>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              key={`${index}-${message.role}`}
            >
              <div
                className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm leading-6 ${
                  message.role === "user"
                    ? "rounded-br-md bg-indigo-600 text-white"
                    : "rounded-bl-md border border-slate-200 bg-white text-slate-700 shadow-sm"
                }`}
              >
                {message.content}
              </div>
            </div>
          ))}
          {busy && (
            <p className="text-sm text-slate-400" aria-live="polite">
              QualBot is thinking…
            </p>
          )}
          <div ref={bottomRef} />
        </div>

        {error && (
          <p className="px-5 pt-3 text-sm text-rose-600" role="alert">{error}</p>
        )}
        <form className="flex gap-3 border-t border-slate-100 p-4" onSubmit={sendMessage}>
          <input
            className="text-input"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Type a message…"
            aria-label="Your message"
            disabled={busy}
          />
          <button className="primary-button" type="submit" disabled={busy || !input.trim()}>
            Send
          </button>
        </form>
      </div>

      <aside className="space-y-5">
        <div className="panel p-5">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="font-semibold text-slate-900">Lead score</h2>
              <p className="mt-1 text-xs text-slate-500">Updates after each reply</p>
            </div>
            <span className={`tier-badge ${tierClass(tier)}`}>{tier}</span>
          </div>
          <div className="mt-6 flex items-end gap-2">
            <span className="text-5xl font-bold tracking-tight text-slate-900">
              {score ?? "—"}
            </span>
            <span className="pb-1 text-sm text-slate-400">/ 100</span>
          </div>
          {action?.url && (
            <a
              className="primary-button mt-5 flex w-full justify-center"
              href={action.url}
              target="_blank"
              rel="noreferrer"
            >
              Book a meeting
            </a>
          )}
        </div>

        <div className="panel p-5">
          <h2 className="font-semibold text-slate-900">BANT qualification</h2>
          <p className="mt-1 text-xs text-slate-500">Captured from the conversation</p>
          <dl className="mt-4 space-y-3">
            {["budget", "authority", "need", "timeline"].map((field) => (
              <div className="flex items-center justify-between gap-3" key={field}>
                <dt className="text-sm capitalize text-slate-500">{field}</dt>
                <dd className="text-right text-sm font-medium text-slate-800">
                  {bant?.[field] || "unknown"}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </aside>
    </section>
  );
}
