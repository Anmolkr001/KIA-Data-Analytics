import React, { useState } from "react";
import { BarChart, Bar, Cell, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { HelpCircle, Filter } from "lucide-react";
import { getFunnelData, groupAndCount, getLostReasonsByModel } from "../utils/dataProcessor";

const COLORS = ["var(--color-kia-blue)", "var(--color-kia-green)", "var(--color-kia-orange)", "var(--color-kia-red)", "#a78bfa", "#f472b6", "#fb7185"];

export default function LeadFunnelStatus({ data }) {
  const [selectedModel, setSelectedModel] = useState("ALL");
  
  const funnelData = getFunnelData(data);
  const statusData = groupAndCount(data, "Enquiry Status", (x) => x || "Active Follow up").slice(0, 7);
  const tdStatusData = groupAndCount(data, "TD Status", (x) => x || "No Appointment Scheduled");
  const lostReasonsByModel = getLostReasonsByModel(data);
  
  // Get all models available for lost reasons filter
  const models = ["ALL", ...Object.keys(lostReasonsByModel).sort()];

  // Filter lost reasons based on selected model
  let lostReasons = [];
  if (selectedModel === "ALL") {
    // Combine lost reasons across all models
    const aggregated = {};
    Object.values(lostReasonsByModel).forEach(list => {
      list.forEach(item => {
        aggregated[item.reason] = (aggregated[item.reason] || 0) + item.count;
      });
    });
    lostReasons = Object.entries(aggregated)
      .map(([reason, count]) => ({ name: reason, value: count }))
      .sort((a,b) => b.value - a.value);
  } else {
    lostReasons = (lostReasonsByModel[selectedModel] || []).map(item => ({
      name: item.reason,
      value: item.count
    }));
  }

  // Slice to top 6 reasons for display
  lostReasons = lostReasons.slice(0, 6);

  return (
    <div className="space-y-6">
      
      {/* Upper Grid: Funnel and Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Module 1: Sourcing/Sales Funnel */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Lead Sourcing & Sales Funnel</h4>
            <p className="text-xs text-kia-muted">Customer drop-off metrics across key stages</p>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                layout="vertical"
                data={funnelData}
                margin={{ top: 10, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#232733" horizontal={false} />
                <XAxis type="number" stroke="var(--color-kia-muted)" fontSize={11} />
                <YAxis type="category" dataKey="name" stroke="var(--color-kia-muted)" fontSize={11} width={120} />
                <Tooltip 
                  contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }}
                  formatter={(value, name, props) => [`${value} Leads (${props.payload.percentage.toFixed(1)}%)`, "Volume"]}
                />
                <Bar dataKey="value" fill="var(--color-kia-red)" radius={[0, 4, 4, 0]}>
                  {funnelData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Module 2: Enquiry Status Distribution */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Enquiry Status Distribution</h4>
            <p className="text-xs text-kia-muted">Current status breakdown in CRM</p>
          </div>
          <div className="h-[300px] w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name.length > 12 ? name.substring(0, 10) + '...' : name} (${(percent * 100).toFixed(0)}%)`}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Lower Grid: TD status & Lost Reasons */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Module 3: Test Drive Outcomes */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white">Test Drive Status Breakdown</h4>
            <p className="text-xs text-kia-muted">Outcomes of scheduled test drive requests</p>
          </div>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={tdStatusData.filter(d => d.name !== "No Appointment Scheduled")}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={11} />
                <YAxis stroke="var(--color-kia-muted)" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                <Bar dataKey="value" fill="var(--color-kia-green)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Module 4: Lost Reason Grouped by Model */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
            <div>
              <h4 className="text-lg font-bold text-white">Top Lost Reasons</h4>
              <p className="text-xs text-kia-muted">Primary drivers for lead cancellations</p>
            </div>
            
            {/* Model Filter */}
            <div className="flex items-center gap-2 bg-white/5 border border-kia-border px-3 py-1.5 rounded-lg text-xs">
              <Filter size={14} className="text-kia-red" />
              <span className="text-kia-muted">Model:</span>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-transparent border-none text-white focus:outline-none font-medium cursor-pointer"
              >
                {models.map(m => (
                  <option key={m} value={m} className="bg-kia-card text-white">{m}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="h-[300px] w-full">
            {lostReasons.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={lostReasons}
                  margin={{ top: 10, right: 30, left: 30, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#232733" horizontal={false} />
                  <XAxis type="number" stroke="var(--color-kia-muted)" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="var(--color-kia-muted)" fontSize={10} width={120} />
                  <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                  <Bar dataKey="value" fill="var(--color-kia-orange)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-kia-muted text-sm">
                No cancellation/lost data recorded for model {selectedModel}.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Funnel Insights Box */}
      <div className="p-5 rounded-lg bg-kia-red/5 border border-kia-red/20 flex gap-4">
        <HelpCircle className="text-kia-red shrink-0 mt-0.5" size={20} />
        <div>
          <h5 className="font-bold text-sm text-white mb-1">Key Insight: The Funnel Bottleneck</h5>
          <p className="text-xs text-kia-muted leading-relaxed">
            The largest drop-off occurs between the <strong>Enquiry</strong> and <strong>Test Drive Scheduled</strong> stages, where <strong>53.4%</strong> of leads are lost. Enforcing a "Test Drive Booking" mandate immediately upon sourcing walk-in or field leads is the highest leverage action to improve dealership conversion.
          </p>
        </div>
      </div>

    </div>
  );
}
