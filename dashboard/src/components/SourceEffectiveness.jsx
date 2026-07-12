import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Award, Compass, LineChart, MessageSquare } from "lucide-react";
import { getSourcePerformance, getCampaignPerformance, getBestSourcePerModel } from "../utils/dataProcessor";

export default function SourceEffectiveness({ data }) {
  const sourcePerf = getSourcePerformance(data);
  const campaignPerf = getCampaignPerformance(data);
  const bestSources = getBestSourcePerModel(data);

  return (
    <div className="space-y-6">
      
      {/* Upper Panel: Campaigns and Best Sourcing Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Campaign performance (Top 10) */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Top 10 Sourcing Campaigns</h4>
            <p className="text-xs text-kia-muted">Campaign lead volume and retail conversion rate</p>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={campaignPerf}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={9} interval={0} tickFormatter={(value) => value.length > 15 ? `${value.substring(0, 12)}...` : value} />
                <YAxis yAxisId="left" stroke="var(--color-kia-blue)" fontSize={10} name="Leads" />
                <YAxis yAxisId="right" orientation="right" stroke="var(--color-kia-red)" fontSize={10} name="Conversion %" unit="%" />
                <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                <Legend verticalAlign="top" height={36} />
                <Bar yAxisId="left" dataKey="leads" name="Leads Generated" fill="var(--color-kia-blue)" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="right" dataKey="conversionRate" name="Conversion Rate %" fill="var(--color-kia-red)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Best Performing Source per Model */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h4 className="text-lg font-bold text-white">Best Performing Sourcing Channel per Model</h4>
              <p className="text-xs text-kia-muted">Sourcing channel yielding the highest conversion rate for each vehicle model</p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase bg-white/[0.01]">
                    <th className="py-2.5 px-3">Vehicle Model</th>
                    <th className="py-2.5 px-3">Best Source Channel</th>
                    <th className="py-2.5 px-3 text-center">Leads</th>
                    <th className="py-2.5 px-3 text-center">Deliveries</th>
                    <th className="py-2.5 px-3 text-right">Conversion Rate</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-kia-border">
                  {bestSources.map((bs, idx) => (
                    <tr key={idx} className="hover:bg-white/[0.01]">
                      <td className="py-2.5 px-3 font-semibold text-white">{bs.model}</td>
                      <td className="py-2.5 px-3 text-kia-text">{bs.bestSource}</td>
                      <td className="py-2.5 px-3 text-center text-kia-muted">{bs.leads}</td>
                      <td className="py-2.5 px-3 text-center text-kia-muted">{bs.retails}</td>
                      <td className="py-2.5 px-3 text-right text-kia-green font-bold">{bs.conversionRate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>

      {/* Lower Panel: Source & Subsource detailed performance table */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="mb-4">
          <h4 className="text-lg font-bold text-white">Channel & Sourcing Performance Matrix</h4>
          <p className="text-xs text-kia-muted">Granular conversion analysis of leads by Source and Sub-source</p>
        </div>

        <div className="overflow-x-auto max-h-[350px] overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-kia-card z-10">
              <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase tracking-wider">
                <th className="py-3 px-4">Source Category</th>
                <th className="py-3 px-4">Sub-source Details</th>
                <th className="py-3 px-4 text-center">Enquiries</th>
                <th className="py-3 px-4 text-center">Test Drives Given</th>
                <th className="py-3 px-4 text-center">Retail Deliveries</th>
                <th className="py-3 px-4 text-center font-bold">TD Rate</th>
                <th className="py-3 px-4 text-right font-bold">Overall Conv. Rate</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-kia-border">
              {sourcePerf.map((s, idx) => (
                <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                  <td className="py-2.5 px-4 font-semibold text-white">{s.source}</td>
                  <td className="py-2.5 px-4 text-kia-text">{s.subSource}</td>
                  <td className="py-2.5 px-4 text-center text-kia-text">{s.leads}</td>
                  <td className="py-2.5 px-4 text-center text-kia-text">{s.tds}</td>
                  <td className="py-2.5 px-4 text-center text-kia-text">{s.retails}</td>
                  <td className="py-2.5 px-4 text-center text-kia-green font-semibold">{s.tdRate}%</td>
                  <td className="py-2.5 px-4 text-right">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      s.conversionRate >= 20 ? 'bg-kia-green/10 text-kia-green border border-kia-green/20' :
                      s.conversionRate >= 10 ? 'bg-kia-blue/10 text-kia-blue border border-kia-blue/20' :
                      'bg-white/5 text-kia-muted border border-kia-border'
                    }`}>
                      {s.conversionRate}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Sourcing insights */}
      <div className="p-5 rounded-lg bg-kia-red/5 border border-kia-red/20 flex gap-4">
        <MessageSquare className="text-kia-red shrink-0 mt-0.5" size={20} />
        <div>
          <h5 className="font-bold text-sm text-white mb-1">Key Insight: Referral Quality Dominance</h5>
          <p className="text-xs text-kia-muted leading-relaxed">
            <strong>Referral</strong> leads exhibit the highest overall conversion quality across almost all models, averaging a <strong>27.6%</strong> retail rate. Conversely, <strong>Hyperlocal</strong> campaigns generate significant lead volumes (32% of total) but suffer from very low quality (3.45% CR). Dealer spend should be reallocated from Hyperlocal ads to Referral incentives.
          </p>
        </div>
      </div>

    </div>
  );
}
