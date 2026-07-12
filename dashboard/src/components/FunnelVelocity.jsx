import React from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Clock, PhoneCall, HelpCircle, Activity } from "lucide-react";
import { getAgingDistribution, getFollowupCorrelation, getCustomerTypeComparison } from "../utils/dataProcessor";

export default function FunnelVelocity({ data }) {
  const agingDist = getAgingDistribution(data);
  const followupCorr = getFollowupCorrelation(data);
  const customerTypeComp = getCustomerTypeComparison(data);

  return (
    <div className="space-y-6">
      
      {/* Upper Panel: Followup Count vs Conversion Rate */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
          <div>
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              <PhoneCall className="text-kia-red" size={20} />
              <span>Follow-up Effectiveness Curve</span>
            </h4>
            <p className="text-xs text-kia-muted">Correlation between the number of follow-ups and retail conversion rate</p>
          </div>
        </div>
        
        <div className="h-[280px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={followupCorr}
              margin={{ top: 10, right: 20, left: -20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
              <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={10} name="Followup Count" />
              <YAxis stroke="var(--color-kia-muted)" fontSize={10} unit="%" />
              <Tooltip 
                contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }}
                formatter={(value) => [`${value}%`, "Retail Conversion Rate"]}
              />
              <Line 
                type="monotone" 
                dataKey="conversionRate" 
                name="Conversion Rate" 
                stroke="var(--color-kia-red)" 
                strokeWidth={3} 
                activeDot={{ r: 8 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 p-3 bg-white/5 rounded-lg border border-kia-border flex justify-between text-xs text-kia-muted">
          <span>💡 <strong>Peak Conversion Range:</strong> 2 to 4 follow-ups yields ~17-19% conversion.</span>
          <span>⚠️ <strong>Diminishing Returns:</strong> More than 4 follow-ups drops conversion rate to less than 2%.</span>
        </div>
      </div>

      {/* Lower Panel: Aging Days and Customer Type splits */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Aging days distribution */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
          <div className="mb-4">
            <h4 className="text-lg font-bold text-white flex items-center gap-2">
              <Clock className="text-kia-blue" size={20} />
              <span>Enquiry Aging vs. Conversion</span>
            </h4>
            <p className="text-xs text-kia-muted">Conversion rate compared against lead aging durations</p>
          </div>

          <div className="h-[260px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={agingDist}
                margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={10} />
                <YAxis stroke="var(--color-kia-muted)" fontSize={10} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                <Bar dataKey="conversionRate" name="Conversion Rate %" fill="var(--color-kia-blue)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Customer Type comparison */}
        <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h4 className="text-lg font-bold text-white flex items-center gap-2">
                <Activity className="text-kia-green" size={20} />
                <span>Customer Segment Analysis</span>
              </h4>
              <p className="text-xs text-kia-muted">Retail conversion rate comparison across Customer Types</p>
            </div>

            <div className="h-[220px] w-full mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={customerTypeComp}
                  margin={{ top: 10, right: 10, left: -20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--color-kia-muted)" fontSize={10} />
                  <YAxis stroke="var(--color-kia-muted)" fontSize={10} unit="%" />
                  <Tooltip contentStyle={{ backgroundColor: "var(--color-kia-card)", borderColor: "var(--color-kia-border)", color: "white" }} />
                  <Bar dataKey="conversionRate" name="Conversion Rate %" fill="var(--color-kia-green)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>

      {/* Funnel Velocity Insight Box */}
      <div className="p-5 rounded-lg bg-kia-red/5 border border-kia-red/20 flex gap-4">
        <HelpCircle className="text-kia-red shrink-0 mt-0.5" size={20} />
        <div>
          <h5 className="font-bold text-sm text-white mb-1">Key Insight: The Follow-up Cliff</h5>
          <p className="text-xs text-kia-muted leading-relaxed">
            The data proves that calling customers more than 4 times yields near-zero incremental value, indicating a <strong>"Follow-up Cliff."</strong> Meanwhile, nearly <strong>28% of leads are abandoned</strong> after only 0 or 1 follow-ups (converting at &lt;0.3%). Dealership managers should enforce a strict mandate of exactly <strong>3 follow-ups per lead</strong>, redirecting consultant hours from long-delayed, high-followup leads onto fresh opportunities.
          </p>
        </div>
      </div>

    </div>
  );
}
