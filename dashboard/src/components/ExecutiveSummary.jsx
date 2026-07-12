import React from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { Users, Car, Percent, Hourglass, TrendingUp, Award } from "lucide-react";
import { calculateKPIs, getEnquiryTrend } from "../utils/dataProcessor";

export default function ExecutiveSummary({ data }) {
  const kpis = calculateKPIs(data);
  const trendData = getEnquiryTrend(data);

  // Hardcoded insights matching the detailed analysis report
  const insights = [
    {
      title: "The Test Drive Catalyst",
      text: "Customers who complete a Test Drive are 4.3x more likely to buy (19.1% vs 4.4% retail rate) and 5.1x more likely to book. Test drives drive 79% of all retail deliveries.",
      icon: Car,
      color: "text-kia-green bg-kia-green/10"
    },
    {
      title: "Sourcing Spend Inefficiency",
      text: "Our highest volume channel (Hyperlocal: 32.0% of leads) converts at an abysmal 3.45%. Conversely, our lowest volume channel (Referrals: 15.7% of leads) converts at a top-tier 27.62%.",
      icon: Percent,
      color: "text-kia-red bg-kia-red/10"
    },
    {
      title: "Follow-up Optimization Sweet Spot",
      text: "Conversion peaks sharply at 2 to 4 follow-ups (17.3% to 19.1%). After 4 follow-ups, conversion collapses to < 2.0%. High-aging follow-ups on dead leads waste capacity.",
      icon: TrendingUp,
      color: "text-kia-orange bg-kia-orange/10"
    }
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        
        {/* KPI: Total Enquiries */}
        <div className="p-6 rounded-xl glass-panel flex items-center justify-between shadow-lg">
          <div>
            <p className="text-xs font-semibold text-kia-muted uppercase tracking-wider mb-1">
              Total Enquiries
            </p>
            <h3 className="text-3xl font-extrabold text-white font-outfit">
              {kpis.total.toLocaleString()}
            </h3>
            <p className="text-[11px] text-kia-muted mt-1">Lead database size</p>
          </div>
          <div className="p-3 rounded-lg bg-kia-blue/10 text-kia-blue">
            <Users size={24} />
          </div>
        </div>

        {/* KPI: Test Drive Conversion */}
        <div className="p-6 rounded-xl glass-panel flex items-center justify-between shadow-lg">
          <div>
            <p className="text-xs font-semibold text-kia-muted uppercase tracking-wider mb-1">
              Test Drive Rate
            </p>
            <h3 className="text-3xl font-extrabold text-white font-outfit">
              {kpis.tdRate.toFixed(1)}%
            </h3>
            <p className="text-[11px] text-kia-green mt-1">
              Goal: &gt; 50% TD compliance
            </p>
          </div>
          <div className="p-3 rounded-lg bg-kia-green/10 text-kia-green">
            <Car size={24} />
          </div>
        </div>

        {/* KPI: Overall Conversion */}
        <div className="p-6 rounded-xl glass-panel flex items-center justify-between shadow-lg">
          <div>
            <p className="text-xs font-semibold text-kia-muted uppercase tracking-wider mb-1">
              Overall Conversion
            </p>
            <h3 className="text-3xl font-extrabold text-white font-outfit">
              {kpis.retailRate.toFixed(1)}%
            </h3>
            <p className="text-[11px] text-kia-red mt-1">Enquiry-to-Retail Delivery</p>
          </div>
          <div className="p-3 rounded-lg bg-kia-red/10 text-kia-red">
            <Percent size={24} />
          </div>
        </div>

        {/* KPI: Avg Aging Days */}
        <div className="p-6 rounded-xl glass-panel flex items-center justify-between shadow-lg">
          <div>
            <p className="text-xs font-semibold text-kia-muted uppercase tracking-wider mb-1">
              Avg Enquiry Aging
            </p>
            <h3 className="text-3xl font-extrabold text-white font-outfit">
              {kpis.avgAging.toFixed(1)} Days
            </h3>
            <p className="text-[11px] text-kia-orange mt-1">Average pipeline speed</p>
          </div>
          <div className="p-3 rounded-lg bg-kia-orange/10 text-kia-orange">
            <Hourglass size={24} />
          </div>
        </div>

      </div>

      {/* Main Graph: Trend Chart */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h4 className="text-lg font-bold text-white">Enquiry Trend over Time</h4>
            <p className="text-xs text-kia-muted">Chronological count of incoming inquiries and retail conversions</p>
          </div>
        </div>

        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={trendData}
              margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="enquiryGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02}/>
                </linearGradient>
                <linearGradient id="retailGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ea1537" stopOpacity={0.35}/>
                  <stop offset="95%" stopColor="#ea1537" stopOpacity={0.02}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
              <XAxis 
                dataKey="date" 
                stroke="var(--color-kia-muted)" 
                fontSize={11}
                tickLine={false}
                axisLine={{ stroke: '#232733' }}
              />
              <YAxis 
                stroke="var(--color-kia-muted)" 
                fontSize={11}
                tickLine={false}
                allowDecimals={false}
                domain={[0, 'auto']}
                axisLine={{ stroke: '#232733' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#151720', 
                  borderColor: '#232733',
                  borderRadius: '10px',
                  color: '#f3f4f6',
                  fontSize: '12px',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.4)'
                }}
                labelStyle={{ color: '#9ca3af', fontWeight: 600, marginBottom: 4 }}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px', color: '#9ca3af', paddingTop: '12px' }}
                iconType="circle"
                iconSize={8}
              />
              <Area 
                type="monotone" 
                dataKey="enquiries" 
                name="Enquiries" 
                stroke="#3b82f6" 
                fillOpacity={1} 
                fill="url(#enquiryGrad)" 
                strokeWidth={2.5}
                dot={{ fill: '#3b82f6', r: 4, strokeWidth: 2, stroke: '#151720' }}
                activeDot={{ fill: '#3b82f6', r: 6, strokeWidth: 2, stroke: '#ffffff' }}
              />
              <Area 
                type="monotone" 
                dataKey="retails" 
                name="Retail Deliveries" 
                stroke="#ea1537" 
                fillOpacity={1} 
                fill="url(#retailGrad)" 
                strokeWidth={2.5}
                dot={{ fill: '#ea1537', r: 4, strokeWidth: 2, stroke: '#151720' }}
                activeDot={{ fill: '#ea1537', r: 6, strokeWidth: 2, stroke: '#ffffff' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Insights Callouts Section */}
      <div className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg">
        <div className="flex items-center gap-2 mb-4 border-b border-kia-border pb-3">
          <Award className="text-kia-red" size={20} />
          <h4 className="text-lg font-bold text-white">Lead Analyst Strategic Takeaways</h4>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {insights.map((insight, idx) => {
            const Icon = insight.icon;
            return (
              <div key={idx} className="flex gap-4 p-4 rounded-lg bg-white/[0.02] border border-kia-border/50">
                <div className={`p-3 rounded-lg shrink-0 h-11 w-11 flex items-center justify-center ${insight.color}`}>
                  <Icon size={20} />
                </div>
                <div>
                  <h5 className="font-bold text-sm text-white mb-1">{insight.title}</h5>
                  <p className="text-xs text-kia-muted leading-relaxed">{insight.text}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
