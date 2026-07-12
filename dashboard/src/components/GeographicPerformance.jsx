import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { MapPin, Globe, Compass, Landmark } from "lucide-react";
import { getGeographicPerformance } from "../utils/dataProcessor";

export default function GeographicPerformance({ data }) {
  const geoData = getGeographicPerformance(data);
  const topRegions = geoData.slice(0, 10);

  return (
    <div className="space-y-6">
      
      {/* Upper Panel: Regional dual axis chart */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="mb-4">
          <h4 className="text-lg font-bold text-white">Top 10 Regions by Lead Volume & Conversion Rate</h4>
          <p className="text-xs text-kia-muted">Comparison of regional market interest and sales conversion efficiency</p>
        </div>
        
        <div className="h-[320px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={topRegions}
              margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
              <XAxis dataKey="key" stroke="var(--color-kia-muted)" fontSize={9} />
              <YAxis yAxisId="left" stroke="var(--color-kia-blue)" fontSize={10} name="Enquiries" />
              <YAxis yAxisId="right" orientation="right" stroke="var(--color-kia-red)" fontSize={10} name="Conversion %" unit="%" />
              <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
              <Legend verticalAlign="top" height={36} />
              <Bar yAxisId="left" dataKey="leads" name="Enquiries" fill="var(--color-kia-blue)" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="conversionRate" name="Conversion Rate %" fill="var(--color-kia-red)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Lower Panel: Heatmap-style ranked table */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="mb-4">
          <h4 className="text-lg font-bold text-white">Geographic Market Penetration Index</h4>
          <p className="text-xs text-kia-muted">Ranked performance table of top municipal and suburban territories</p>
        </div>

        <div className="overflow-x-auto max-h-[350px] overflow-y-auto">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-kia-card z-10">
              <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase tracking-wider bg-white/[0.01]">
                <th className="py-3 px-4">Territory (City)</th>
                <th className="py-3 px-4">State Location</th>
                <th className="py-3 px-4 text-center">Enquiries Sourced</th>
                <th className="py-3 px-4 text-center">Retail Deliveries</th>
                <th className="py-3 px-4 text-right">Conversion Rate</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-kia-border">
              {geoData.map((region, idx) => (
                <tr key={idx} className="hover:bg-white/[0.01] transition-colors">
                  <td className="py-2.5 px-4 font-semibold text-white flex items-center gap-2">
                    <MapPin size={14} className="text-kia-red" />
                    <span>{region.city}</span>
                  </td>
                  <td className="py-2.5 px-4 text-kia-muted">{region.state}</td>
                  <td className="py-2.5 px-4 text-center text-kia-text">{region.leads}</td>
                  <td className="py-2.5 px-4 text-center text-kia-text">{region.retails}</td>
                  <td className="py-2.5 px-4 text-right font-bold">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      region.conversionRate >= 15 ? 'text-kia-green bg-kia-green/10' :
                      region.conversionRate >= 8 ? 'text-kia-blue bg-kia-blue/10' :
                      'text-kia-muted bg-white/5'
                    }`}>
                      {region.conversionRate}%
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
        <Globe className="text-kia-red shrink-0 mt-0.5" size={20} />
        <div>
          <h5 className="font-bold text-sm text-white mb-1">Key Insight: Regional Core Sourcing</h5>
          <p className="text-xs text-kia-muted leading-relaxed">
            The dealership's core business is heavily concentrated in <strong>BHUBANESWAR</strong>, yielding over <strong>62%</strong> of lead volume. Sourcing in outer suburban areas like Cuttack and Puri shows strong conversion rates (averaging &gt;11.5%), which suggests high-quality suburban demand. Expanding targeted satellite marketing centers in these outer rings represents an untapped market opportunity.
          </p>
        </div>
      </div>

    </div>
  );
}
