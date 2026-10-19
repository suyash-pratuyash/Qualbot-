import { useEffect, useState } from "react";
import { requestApi } from "./api";

function tierClass(tier) {
  if (tier === "hot") return "tier-hot";
  if (tier === "warm") return "tier-warm";
  return "tier-cold";
}

export default function Dashboard({ adminKey }) {
  const [leads, setLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pageOffset, setPageOffset] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  async function loadLeads(offset = 0) {
    setLoading(true);
    setError("");
    try {
      const page = await requestApi(`/leads?limit=100&offset=${offset}`, {
        headers: { "X-Admin-Key": adminKey },
      });
      setLeads(page);
      setPageOffset(offset);
      setHasMore(page.length === 100);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLeads();
  }, [adminKey]);

  async function selectLead(sessionId) {
    setError("");
    try {
      setSelectedLead(
        await requestApi(`/leads/${encodeURIComponent(sessionId)}`, {
          headers: { "X-Admin-Key": adminKey },
        }),
      );
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">Lead dashboard</h2>
          <p className="mt-1 text-sm text-slate-500">
            Select a lead to inspect its qualification and conversation.
          </p>
        </div>
        <button className="secondary-button" onClick={() => loadLeads(pageOffset)}>
          Refresh leads
        </button>
      </div>

      {error && (
        <p className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700" role="alert">
          Could not load data: {error}
        </p>
      )}

      <div className="panel overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100 text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3 font-semibold">Session</th>
              <th className="px-4 py-3 font-semibold">Score</th>
              <th className="px-4 py-3 font-semibold">Tier</th>
              <th className="px-4 py-3 font-semibold">Budget</th>
              <th className="px-4 py-3 font-semibold">Authority</th>
              <th className="px-4 py-3 font-semibold">Need</th>
              <th className="px-4 py-3 font-semibold">Timeline</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {leads.map((lead) => (
              <tr
                className={`cursor-pointer transition hover:bg-indigo-50/60 ${
                  selectedLead?.session_id === lead.session_id ? "bg-indigo-50" : ""
                }`}
                key={lead.session_id}
                onClick={() => selectLead(lead.session_id)}
              >
                <td className="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-700">
                  {lead.session_id}
                </td>
                <td className="px-4 py-3 font-semibold text-slate-900">{lead.score}</td>
                <td className="px-4 py-3">
                  <span className={`tier-badge ${tierClass(lead.tier)}`}>{lead.tier}</span>
                </td>
                {["budget", "authority", "need", "timeline"].map((field) => (
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600" key={field}>
                    {lead.bant?.[field] || "unknown"}
                  </td>
                ))}
              </tr>
            ))}
            {!loading && leads.length === 0 && (
              <tr>
                <td className="px-4 py-10 text-center text-slate-500" colSpan="7">
                  No leads saved yet. Start a conversation in the Chat tab.
                </td>
              </tr>
            )}
            {loading && (
              <tr>
                <td className="px-4 py-10 text-center text-slate-500" colSpan="7">
                  Loading leads…
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <button
          className="secondary-button"
          disabled={loading || pageOffset === 0}
          onClick={() => loadLeads(Math.max(0, pageOffset - 100))}
        >
          Previous
        </button>
        <span className="text-xs text-slate-500">
          {leads.length ? `Leads ${pageOffset + 1}–${pageOffset + leads.length}` : "No leads"}
        </span>
        <button
          className="secondary-button"
          disabled={loading || !hasMore}
          onClick={() => loadLeads(pageOffset + 100)}
        >
          Next
        </button>
      </div>

      {selectedLead && (
        <div className="panel p-5">
          <div className="mb-4 border-b border-slate-100 pb-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600">
              Conversation transcript
            </p>
            <h3 className="mt-1 break-all font-mono text-sm text-slate-700">
              {selectedLead.session_id}
            </h3>
          </div>
          <div className="max-h-[440px] space-y-3 overflow-y-auto">
            {selectedLead.transcript.map((message) => (
              <div
                className={`rounded-xl p-3 ${
                  message.role === "user"
                    ? "ml-8 bg-indigo-50 text-slate-800"
                    : "mr-8 bg-slate-50 text-slate-700"
                }`}
                key={message.id}
              >
                <div className="mb-1 flex justify-between gap-3 text-xs text-slate-500">
                  <span className="font-semibold capitalize">{message.role}</span>
                  <time>{new Date(message.ts).toLocaleString()}</time>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6">{message.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
