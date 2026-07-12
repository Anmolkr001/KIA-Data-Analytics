import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { Users, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { getConsultantPerformance } from "../utils/dataProcessor";

export default function ConsultantPerformance({ data }) {
  const consultants = getConsultantPerformance(data);

  // Top consultant statistics
  const topPerformer = consultants[0] || null;
  const flaggedCount = consultants.filter(c => c.efficiencyGap).length;

  return (
    <div className="space-y-6">
      
      {/* Upper Panel: KPI stats & Ranked Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quick Performance Indicators */}
        <div className="flex flex-col gap-4 lg:col-span-1">
          {/* Top Performer Card */}
          {topPerformer && (
            <div className="p-6 rounded-xl glass-panel border border-kia-border flex items-center gap-4 shadow-lg">
              <div className="p-3 bg-kia-green/10 text-kia-green rounded-lg shrink-0">
                <CheckCircle size={24} />
              </div>
              <div>
                <p className="text-xs text-kia-muted uppercase tracking-wider font-semibold">Top Retail Consultant</p>
                <h4 className="text-lg font-bold text-white mt-0.5">{topPerformer.name}</h4>
                <p className="text-xs text-kia-muted mt-1">
                  Delivered <span className="text-kia-green font-bold">{topPerformer.retails} cars</span> ({topPerformer.conversion}% CR)
                </p>
              </div>
            </div>
          )}

          {/* Efficiency Flags Card */}
          <div className="p-6 rounded-xl glass-panel border border-kia-border flex items-center gap-4 shadow-lg">
            <div className={`p-3 rounded-lg shrink-0 ${flaggedCount > 0 ? 'bg-kia-red/10 text-kia-red' : 'bg-kia-green/10 text-kia-green'}`}>
              <AlertTriangle size={24} />
            </div>
            <div>
              <p className="text-xs text-kia-muted uppercase tracking-wider font-semibold">Efficiency Gap Flags</p>
              <h4 className="text-lg font-bold text-white mt-0.5">{flaggedCount} Consultants</h4>
              <p className="text-xs text-kia-muted mt-1">
                {flaggedCount > 0 
                  ? "Avg follow-ups &gt;= 4.0 but conversion &lt; 8.0%" 
                  : "All active consultants meeting baseline criteria"}
              </p>
            </div>
          </div>
        </div>

        {/* Bar Chart: Conversion Rate Leaderboard */}
        <div className="lg:col-span-2 p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Consultant Conversion Leaderboard (%)</h4>
            <p className="text-xs text-kia-muted">Ranked list of sales consultants by lead-to-delivery conversion rate</p>
          </div>
          <div className="h-[220px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={consultants.slice(0, 10)}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={9} />
                <YAxis stroke="var(--color-kia-muted)" fontSize={10} unit="%" />
                <Tooltip 
                  contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }}
                  formatter={(value) => [`${value}%`, "Conversion Rate"]}
                />
                <Bar dataKey="conversion" fill="var(--color-kia-red)" radius={[4, 4, 0, 0]}>
                  {consultants.slice(0, 10).map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.efficiencyGap ? "var(--color-kia-orange)" : "var(--color-kia-red)"} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Lower Panel: Performance Table */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="mb-4">
          <h4 className="text-lg font-bold text-white">All Consultant Performance Metrics</h4>
          <p className="text-xs text-kia-muted">Details on leads handled, conversion output, and sales efforts</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase tracking-wider bg-white/[0.01]">
                <th className="py-3 px-4">Consultant Name</th>
                <th className="py-3 px-4 text-center">Leads Handled</th>
                <th className="py-3 px-4 text-center">Retail Deliveries</th>
                <th className="py-3 px-4 text-center">Conversion %</th>
                <th className="py-3 px-4 text-center">Avg Follow-ups</th>
                <th className="py-3 px-4 text-center">Avg Aging Days</th>
                <th className="py-3 px-4 text-right">Status Flag</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-kia-border">
              {consultants.map((c, idx) => (
                <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-white">{c.name}</td>
                  <td className="py-3.5 px-4 text-center text-kia-text">{c.leads}</td>
                  <td className="py-3.5 px-4 text-center text-kia-text">{c.retails}</td>
                  <td className="py-3.5 px-4 text-center">
                    <span className={`font-semibold ${c.conversion >= 15 ? 'text-kia-green' : c.conversion >= 8 ? 'text-white' : 'text-kia-muted'}`}>
                      {c.conversion}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-center text-kia-text">{c.avgFollowup}</td>
                  <td className="py-3.5 px-4 text-center text-kia-text">{c.avgAging}</td>
                  <td className="py-3.5 px-4 text-right">
                    {c.efficiencyGap ? (
                      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-bold bg-kia-orange/10 text-kia-orange border border-kia-orange/20 animate-pulse">
                        <AlertTriangle size={12} />
                        Efficiency Gap
                      </span>
                    ) : c.conversion >= 15 ? (
                      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-bold bg-kia-green/10 text-kia-green border border-kia-green/20">
                        Top Performer
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[11px] font-bold bg-white/5 text-kia-muted border border-kia-border">
                        Standard
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Consultant insights */}
      <div className="p-5 rounded-lg bg-kia-red/5 border border-kia-red/20 flex gap-4">
        <TrendingUp className="text-kia-red shrink-0 mt-0.5" size={20} />
        <div>
          <h5 className="font-bold text-sm text-white mb-1">Key Insight: Leaderboard Disparity</h5>
          <p className="text-xs text-kia-muted leading-relaxed">
            The top consultant, <strong>RAJ KUMAR JENA</strong>, converts lead traffic at nearly <strong>29.2%</strong>, 2.5x the dealership average. High-yield consultants secure conversions by enforcing strict test drive bookings early in the cycle, whereas consultants flagged with an <strong>"Efficiency Gap"</strong> average more than 4 follow-ups with less than 8% conversion, indicating wasted follow-up capacity on low-quality leads.
          </p>
        </div>
      </div>

    </div>
  );
}
