import { useEffect, useState } from "react";
import { requestApi } from "./api";

/**
 * Helper to pick color styles based on lead tier
 */
function getTierBadgeClass(tier) {
  if (tier === "hot") return "bg-rose-100 text-rose-700 border border-rose-200";
  if (tier === "warm") return "bg-amber-100 text-amber-700 border border-amber-200";
  return "bg-sky-100 text-sky-700 border border-sky-200";
}

export default function Dashboard() {
  // -------------------------------------------------------------
  // 1. STATE MANAGEMENT
  // -------------------------------------------------------------

  // Array of leads returned from GET /leads
  const [leads, setLeads] = useState([]);

  // Detailed lead object selected by user (includes full transcript)
  const [selectedLead, setSelectedLead] = useState(null);

  // Loading and error indicators
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // -------------------------------------------------------------
  // 2. API CALLS
  // -------------------------------------------------------------

  // Fetch all qualified leads from FastAPI backend
  async function fetchLeads() {
    setLoading(true);
    setError("");
    try {
      const data = await requestApi("/leads?limit=100");
      setLeads(data);
    } catch (err) {
      setError(err.message || "Failed to load leads from backend.");
    } finally {
      setLoading(false);
    }
  }

  // Fetch full conversation transcript for a specific lead session
  async function handleSelectLead(sessionId) {
    try {
      const leadDetail = await requestApi(`/leads/${encodeURIComponent(sessionId)}`);
      setSelectedLead(leadDetail);
    } catch (err) {
      setError(`Could not load transcript: ${err.message}`);
    }
  }

  // Load leads on initial component mount
  useEffect(() => {
    fetchLeads();
  }, []);

  // Summary counts for mentor presentation
  const hotCount = leads.filter((l) => l.tier === "hot").length;
  const warmCount = leads.filter((l) => l.tier === "warm").length;
  const coldCount = leads.filter((l) => l.tier === "cold").length;

  // -------------------------------------------------------------
  // 3. UI RENDER
  // -------------------------------------------------------------
  return (
    <div className="space-y-6">
      {/* Header & Quick Stats Row */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Lead Dashboard</h2>
          <p className="text-xs text-slate-500 mt-1">
            Overview of all qualified leads and their full conversation transcripts.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Quick Metrics */}
          <div className="hidden md:flex items-center gap-2 text-xs font-medium">
            <span className="px-2.5 py-1 rounded-lg bg-rose-50 text-rose-700 border border-rose-100">
              Hot: {hotCount}
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 border border-amber-100">
              Warm: {warmCount}
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-sky-50 text-sky-700 border border-sky-100">
              Cold: {coldCount}
            </span>
          </div>

          <button
            onClick={fetchLeads}
            disabled={loading}
            className="px-3.5 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-200 rounded-xl hover:border-indigo-300 hover:text-indigo-600 transition shadow-xs"
          >
            {loading ? "Refreshing..." : "↻ Refresh"}
          </button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 font-medium">
          {error}
        </div>
      )}

      {/* Main Leads Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100 text-slate-500 uppercase tracking-wider font-semibold">
                <th className="py-3 px-4">Session ID</th>
                <th className="py-3 px-4">Score</th>
                <th className="py-3 px-4">Tier</th>
                <th className="py-3 px-4">Budget</th>
                <th className="py-3 px-4">Authority</th>
                <th className="py-3 px-4">Need</th>
                <th className="py-3 px-4">Timeline</th>
                <th className="py-3 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {leads.map((lead) => {
                const isSelected = selectedLead?.session_id === lead.session_id;
                return (
                  <tr
                    key={lead.session_id}
                    onClick={() => handleSelectLead(lead.session_id)}
                    className={`cursor-pointer transition hover:bg-indigo-50/50 ${
                      isSelected ? "bg-indigo-50/80 font-medium" : ""
                    }`}
                  >
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                      {lead.session_id}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">{lead.score}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold uppercase ${getTierBadgeClass(lead.tier)}`}>
                        {lead.tier}
                      </span>
                    </td>
                    <td className="py-3 px-4 capitalize">{lead.bant?.budget || "unknown"}</td>
                    <td className="py-3 px-4 capitalize">
                      {(lead.bant?.authority || "unknown").replace("_", " ")}
                    </td>
                    <td className="py-3 px-4 capitalize">{lead.bant?.need || "unknown"}</td>
                    <td className="py-3 px-4 capitalize">{lead.bant?.timeline || "unknown"}</td>
                    <td className="py-3 px-4 text-slate-400">
                      {lead.created_at ? new Date(lead.created_at).toLocaleDateString() : "—"}
                    </td>
                  </tr>
                );
              })}

              {!loading && leads.length === 0 && (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    No leads recorded yet. Go to the Chat tab and send a message!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Lead Conversation Transcript View */}
      {selectedLead && (
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-4">
            <div>
              <p className="text-xs uppercase tracking-wider font-bold text-indigo-600">
                Conversation Transcript
              </p>
              <h3 className="text-sm font-semibold text-slate-800 font-mono mt-0.5">
                {selectedLead.session_id}
              </h3>
            </div>
            <div className="flex items-center gap-2 mt-2 sm:mt-0">
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${getTierBadgeClass(selectedLead.tier)}`}>
                {selectedLead.tier} ({selectedLead.score} pts)
              </span>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-xs text-slate-400 hover:text-slate-600 px-2 py-1"
              >
                ✕ Close
              </button>
            </div>
          </div>

          {/* Transcript Message List */}
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {selectedLead.transcript?.map((msg, i) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={i}
                  className={`p-3.5 rounded-xl border text-xs leading-relaxed ${
                    isUser
                      ? "bg-indigo-50 border-indigo-100 text-indigo-950 ml-6"
                      : "bg-slate-50 border-slate-200 text-slate-800 mr-6"
                  }`}
                >
                  <div className="flex items-center justify-between font-semibold mb-1 text-[11px] text-slate-500">
                    <span className="capitalize">{msg.role}</span>
                    <span>{msg.ts ? new Date(msg.ts).toLocaleTimeString() : ""}</span>
                  </div>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
