import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Sparkles, Car, Landmark, ArrowRightLeft } from "lucide-react";
import { getModelPerformance, getPriceDistribution, getOEMComparison, getPresentCarSplit } from "../utils/dataProcessor";

export default function ModelInsights({ data }) {
  const modelPerf = getModelPerformance(data);
  const priceDist = getPriceDistribution(data);
  const oemCompare = getOEMComparison(data);
  const tradeInSplit = getPresentCarSplit(data);

  return (
    <div className="space-y-6">
      
      {/* Upper Grid: Model Table */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="mb-4">
          <h4 className="text-lg font-bold text-white">Vehicle Model Demand & Conversion Performance</h4>
          <p className="text-xs text-kia-muted">Comparison of sales volumes, test drive compliance, and top configurations</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase bg-white/[0.01]">
                <th className="py-3 px-4">Model Name</th>
                <th className="py-3 px-4 text-center">Enquiries</th>
                <th className="py-3 px-4 text-center">Test Drives Given</th>
                <th className="py-3 px-4 text-center">TD Rate</th>
                <th className="py-3 px-4 text-center">Retail Deliveries</th>
                <th className="py-3 px-4 text-center font-bold">Conversion Rate</th>
                <th className="py-3 px-4">Primary Variant Class</th>
                <th className="py-3 px-4">Fuel Type Mix</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-kia-border">
              {modelPerf.map((m, idx) => (
                <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                  <td className="py-3 px-4 font-bold text-white">{m.model}</td>
                  <td className="py-3 px-4 text-center text-kia-text">{m.leads}</td>
                  <td className="py-3 px-4 text-center text-kia-text">{m.tds}</td>
                  <td className="py-3 px-4 text-center text-kia-blue font-semibold">{m.tdRate}%</td>
                  <td className="py-3 px-4 text-center text-kia-text">{m.retails}</td>
                  <td className="py-3 px-4 text-center font-bold text-kia-red">{m.conversionRate}%</td>
                  <td className="py-3 px-4 text-xs text-kia-muted max-w-xs truncate" title={m.topVariants}>
                    {m.topVariants}
                  </td>
                  <td className="py-3 px-4 text-xs text-kia-muted">{m.topFuel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Middle Grid: Price and Trade-in Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Expected Price distribution by Model */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Expected Price Distribution (INR)</h4>
            <p className="text-xs text-kia-muted">Median customer budget expectations across models (excludes blanks/zeros)</p>
          </div>
          <div className="h-[280px] w-full">
            {priceDist.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={priceDist.slice(0, 6)}
                  margin={{ top: 10, right: 10, left: 10, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                  <XAxis dataKey="model" stroke="var(--color-kia-muted)" fontSize={10} />
                  <YAxis stroke="var(--color-kia-muted)" fontSize={10} tickFormatter={(val) => `₹${(val / 100000).toFixed(1)}L`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }}
                    formatter={(value) => [`₹${value.toLocaleString()}`, "Median Expected Price"]}
                  />
                  <Bar dataKey="median" fill="var(--color-kia-green)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-kia-muted text-sm">
                No pricing survey responses available in the current subset.
              </div>
            )}
          </div>
        </div>

        {/* Trade-in Trade Split */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h4 className="text-lg font-bold text-white">Trade-In Segment Conversion Impact</h4>
              <p className="text-xs text-kia-muted">Comparison of customer segments with an existing car vs. fresh buyers</p>
            </div>
            
            <div className="grid grid-cols-2 gap-4 my-6">
              {tradeInSplit.map((split, idx) => (
                <div key={idx} className="p-5 rounded-xl bg-white/[0.02] border border-kia-border text-center">
                  <p className="text-xs text-kia-muted font-semibold uppercase">{split.name}</p>
                  <h3 className="text-3xl font-extrabold text-white font-outfit mt-2">{split.count.toLocaleString()} Leads</h3>
                  <div className="mt-3 flex items-center justify-center gap-1.5 text-sm font-bold text-kia-red">
                    <ArrowRightLeft size={16} />
                    <span>{split.conversionRate}% CR</span>
                  </div>
                  <p className="text-[10px] text-kia-muted mt-1">{split.retails} deliveries completed</p>
                </div>
              ))}
            </div>
          </div>

          <p className="text-xs text-kia-muted leading-relaxed italic bg-white/5 p-3 rounded-lg border border-kia-border">
            Customers with a trade-in car represent a warm sales segment because they have immediate replacement intent, converting at higher rates if exchange values align.
          </p>
        </div>

      </div>

      {/* Competitor Cross-shop */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* OEM Cross-shopping */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Competitor Cross-Shopping Analysis</h4>
            <p className="text-xs text-kia-muted">Top original vehicle models owned by customers planning trade-ins</p>
          </div>
          <div className="h-[280px] w-full">
            {oemCompare.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={oemCompare}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 30, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#232733" horizontal={false} />
                  <XAxis type="number" stroke="var(--color-kia-muted)" fontSize={10} />
                  <YAxis type="category" dataKey="name" stroke="var(--color-kia-muted)" fontSize={10} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                  <Bar dataKey="count" fill="var(--color-kia-orange)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-kia-muted text-sm">
                No competitor exchange data recorded in the current dataset.
              </div>
            )}
          </div>
        </div>

        {/* Product Insight Callout */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="text-kia-red" size={20} />
              <h4 className="text-lg font-bold text-white">Lead Analyst Product Notes</h4>
            </div>
            <ul className="space-y-3.5 text-xs text-kia-muted leading-relaxed">
              <li>
                <strong className="text-white">Kia Sonet Dominance:</strong> Sonet is our dealership's undisputed star, generating high volume (2,115 leads) and the highest segment conversion rate of <strong className="text-kia-green">16.3%</strong>, accounting for 44% of total sales.
              </li>
              <li>
                <strong className="text-white">Kia Carens Performance:</strong> The Carens MPV converts exceptionally well (<strong className="text-kia-green">14.7% CR</strong>), illustrating heavy family segment demand in Bhubaneswar.
              </li>
              <li>
                <strong className="text-white">New Seltos Inefficiency:</strong> Although Seltos draws the highest customer interest (2,155 leads), it converts at a low <strong className="text-kia-red">8.68% CR</strong>. Consultants are struggling to move prospects from interest to delivery, suggesting heavy competition or feature/pricing mismatches.
              </li>
            </ul>
          </div>
        </div>

      </div>

    </div>
  );
}
