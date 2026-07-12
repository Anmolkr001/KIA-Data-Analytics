import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  TrendingUp,
  Users,
  CalendarDays,
  Search,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  BarChart3,
  Building2,
  User,
} from "lucide-react";

// Color-blind friendly palette (Wong palette + KIA brand)
const DONUT_COLORS = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#ec4899"];

// ──────────────────────────────────────────────
//  Animated Number Counter Hook
// ──────────────────────────────────────────────
function useCountUp(target, duration = 1200) {
  const [count, setCount] = useState(0);
  const prevTarget = useRef(0);

  useEffect(() => {
    if (target === null || target === undefined || isNaN(target)) return;

    const start = prevTarget.current;
    const end = Number(target);
    const startTime = performance.now();

    function animate(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start + (end - start) * eased);
      setCount(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        prevTarget.current = end;
      }
    }

    requestAnimationFrame(animate);
  }, [target, duration]);

  return count;
}

// ──────────────────────────────────────────────
//  KPI Card Sub-component
// ──────────────────────────────────────────────
function KPICard({ title, value, subtitle, icon: Icon, accentClass, ariaLabel, animDelay, isNumeric = false }) {
  const animatedValue = useCountUp(isNumeric ? value : 0);
  const displayValue = isNumeric ? animatedValue.toLocaleString() : value;

  return (
    <div
      className={`p-6 rounded-xl glass-panel flex items-center justify-between shadow-lg kpi-card-glow animate-fade-in-up ${animDelay}`}
      role="region"
      aria-label={ariaLabel}
    >
      <div>
        <p className="text-xs font-semibold text-kia-muted uppercase tracking-wider mb-1">
          {title}
        </p>
        <h3 className="text-3xl font-extrabold text-[var(--color-kia-text)] font-outfit">
          {displayValue}
        </h3>
        <p className={`text-[11px] mt-1 ${accentClass || "text-kia-muted"}`}>{subtitle}</p>
      </div>
      <div className={`p-3 rounded-lg ${
        accentClass?.includes("green") ? "bg-kia-green/10 text-kia-green" :
        accentClass?.includes("orange") ? "bg-kia-orange/10 text-kia-orange" :
        accentClass?.includes("red") ? "bg-kia-red/10 text-kia-red" :
        "bg-kia-blue/10 text-kia-blue"
      }`}>
        <Icon size={24} aria-hidden="true" />
      </div>
    </div>
  );
}

// ──────────────────────────────────────────────
//  Sortable Table Header
// ──────────────────────────────────────────────
function SortableHeader({ label, column, currentSort, currentOrder, onSort }) {
  const isActive = currentSort === column;
  const nextOrder = isActive && currentOrder === "asc" ? "desc" : "asc";

  return (
    <th
      className="py-3 px-4 cursor-pointer select-none hover:bg-white/[0.03] transition-colors"
      onClick={() => onSort(column, nextOrder)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSort(column, nextOrder);
        }
      }}
      tabIndex={0}
      role="columnheader"
      aria-sort={isActive ? (currentOrder === "asc" ? "ascending" : "descending") : "none"}
      aria-label={`Sort by ${label}`}
    >
      <span className="inline-flex items-center gap-1.5">
        {label}
        {isActive ? (
          currentOrder === "asc" ? (
            <ArrowUp size={12} className="text-kia-red" />
          ) : (
            <ArrowDown size={12} className="text-kia-red" />
          )
        ) : (
          <ArrowUpDown size={12} className="text-kia-muted/40" />
        )}
      </span>
    </th>
  );
}

// ──────────────────────────────────────────────
//  Custom Tooltip for Charts
// ──────────────────────────────────────────────
function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || payload.length === 0) return null;
  return (
    <div className="glass-panel rounded-lg px-4 py-3 shadow-xl border border-kia-border">
      <p className="text-xs font-semibold text-[var(--color-kia-text)] mb-1">{label}</p>
      {payload.map((entry, idx) => (
        <p key={idx} className="text-xs text-kia-muted">
          <span className="inline-block w-2 h-2 rounded-full mr-2" style={{ backgroundColor: entry.color }} />
          {entry.name}: <strong className="text-[var(--color-kia-text)]">{entry.value.toLocaleString()}</strong>
        </p>
      ))}
    </div>
  );
}

// ──────────────────────────────────────────────
//  Donut Center Label
// ──────────────────────────────────────────────
function DonutCenterLabel({ viewBox, total }) {
  if (!viewBox) return null;
  const { cx, cy } = viewBox;
  return (
    <g>
      <text x={cx} y={cy - 8} textAnchor="middle" dominantBaseline="central"
        style={{ fontSize: "28px", fontWeight: 800, fill: "var(--color-kia-text)", fontFamily: "Outfit" }}>
        {total?.toLocaleString() ?? "—"}
      </text>
      <text x={cx} y={cy + 16} textAnchor="middle" dominantBaseline="central"
        style={{ fontSize: "11px", fontWeight: 500, fill: "var(--color-kia-muted)" }}>
        Total
      </text>
    </g>
  );
}

// ──────────────────────────────────────────────
//  Local Data Computation Helpers
// ──────────────────────────────────────────────

function computeKPIs(data) {
  const total = data.length;
  const typeCounts = {};
  const dateCounts = {};

  for (const row of data) {
    // Customer type counts
    const cType = (row["Customer Type"] || "Individual").toString().trim().toLowerCase();
    const normalizedType = cType.charAt(0).toUpperCase() + cType.slice(1);
    typeCounts[normalizedType] = (typeCounts[normalizedType] || 0) + 1;

    // Date counts for peak day
    const rawDate = row["Enquiry Date"];
    if (rawDate) {
      const dateStr = String(rawDate).slice(0, 10);
      dateCounts[dateStr] = (dateCounts[dateStr] || 0) + 1;
    }
  }

  const individualCount = typeCounts["Individual"] || 0;
  const corporateCount = typeCounts["Corporate"] || 0;

  // Peak day
  let peakDay = "—";
  let peakDayCount = 0;
  for (const [d, c] of Object.entries(dateCounts)) {
    if (c > peakDayCount) {
      peakDayCount = c;
      peakDay = d;
    }
  }

  return {
    total,
    individualCount,
    corporateCount,
    individualPct: total > 0 ? ((individualCount / total) * 100).toFixed(1) : "0",
    corporatePct: total > 0 ? ((corporateCount / total) * 100).toFixed(1) : "0",
    peakDay,
    peakDayCount,
  };
}

function computeTrend(data) {
  const dateCounts = {};
  for (const row of data) {
    const rawDate = row["Enquiry Date"];
    if (rawDate) {
      const dateStr = String(rawDate).slice(0, 10);
      dateCounts[dateStr] = (dateCounts[dateStr] || 0) + 1;
    }
  }
  return Object.entries(dateCounts)
    .map(([period, count]) => ({ period, count }))
    .sort((a, b) => a.period.localeCompare(b.period));
}

function computeTypeBreakdown(data) {
  const total = data.length;
  const counts = {};
  for (const row of data) {
    const cType = (row["Customer Type"] || "Individual").toString().trim();
    const normalized = cType.charAt(0).toUpperCase() + cType.slice(1).toLowerCase();
    counts[normalized] = (counts[normalized] || 0) + 1;
  }
  return Object.entries(counts)
    .map(([type, count]) => ({
      type,
      count,
      percentage: total > 0 ? ((count / total) * 100).toFixed(2) : "0",
    }))
    .sort((a, b) => b.count - a.count);
}

// ──────────────────────────────────────────────
//  Main Component (prop-driven, no API calls)
// ──────────────────────────────────────────────
export default function EnquiryAnalytics({ data }) {
  // ── Local computed data ──
  const kpis = useMemo(() => computeKPIs(data), [data]);
  const trendData = useMemo(() => computeTrend(data), [data]);
  const typeBreakdown = useMemo(() => computeTypeBreakdown(data), [data]);

  // ── Table state ──
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(15);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState("");
  const [sortOrder, setSortOrder] = useState("asc");
  const [customerTypeFilter, setCustomerTypeFilter] = useState("");
  const searchInputRef = useRef(null);

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  // ── Client-side table processing ──
  const tableColumns = [
    { key: "S NO", label: "#" },
    { key: "Enquiry Date", label: "Enquiry Date" },
    { key: "Anonymized Customer ID", label: "Customer ID" },
    { key: "Customer Type", label: "Type" },
    { key: "Model", label: "Model" },
    { key: "Enquiry Status", label: "Status" },
    { key: "Source", label: "Source" },
    { key: "City", label: "City" },
    { key: "Consultant Name", label: "Consultant" },
  ];

  const processedTable = useMemo(() => {
    let view = [...data];

    // Filter by customer type
    if (customerTypeFilter) {
      view = view.filter(
        (row) =>
          (row["Customer Type"] || "").toString().toLowerCase() === customerTypeFilter.toLowerCase()
      );
    }

    // Search across multiple columns
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase();
      view = view.filter((row) => {
        for (const col of ["Anonymized Customer ID", "Model", "City", "Consultant Name", "Customer Type"]) {
          if ((row[col] || "").toString().toLowerCase().includes(q)) return true;
        }
        return false;
      });
    }

    // Sort
    if (sortBy) {
      view.sort((a, b) => {
        const aVal = (a[sortBy] ?? "").toString();
        const bVal = (b[sortBy] ?? "").toString();
        const cmp = aVal.localeCompare(bVal, undefined, { numeric: true, sensitivity: "base" });
        return sortOrder === "asc" ? cmp : -cmp;
      });
    }

    // Pagination
    const totalRecords = view.length;
    const totalPages = Math.max(1, Math.ceil(totalRecords / pageSize));
    const safePage = Math.min(page, totalPages);
    const startIdx = (safePage - 1) * pageSize;
    const pageData = view.slice(startIdx, startIdx + pageSize);

    return { page: safePage, pageSize, totalRecords, totalPages, data: pageData };
  }, [data, customerTypeFilter, debouncedSearch, sortBy, sortOrder, page, pageSize]);

  // Sort handler
  const handleSort = useCallback((column, order) => {
    setSortBy(column);
    setSortOrder(order);
    setPage(1);
  }, []);

  // Page size change handler
  const handlePageSizeChange = useCallback((newSize) => {
    setPageSize(newSize);
    setPage(1);
  }, []);

  return (
    <div className="space-y-6">
      {/* ═══════════════════════════════════════
          KPI Cards Row
         ═══════════════════════════════════════ */}
      <section aria-label="Key Performance Indicators">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          <KPICard
            title="Total Enquiries"
            value={kpis.total}
            subtitle="All recorded leads"
            icon={Users}
            accentClass="text-kia-blue"
            ariaLabel="Total number of enquiries"
            animDelay="animate-delay-1"
            isNumeric={true}
          />
          <KPICard
            title="Individual Leads"
            value={kpis.individualCount}
            subtitle={`${kpis.individualPct}% of total`}
            icon={User}
            accentClass="text-kia-green"
            ariaLabel="Number of individual customer enquiries"
            animDelay="animate-delay-2"
            isNumeric={true}
          />
          <KPICard
            title="Corporate Leads"
            value={kpis.corporateCount}
            subtitle={`${kpis.corporatePct}% of total`}
            icon={Building2}
            accentClass="text-kia-orange"
            ariaLabel="Number of corporate customer enquiries"
            animDelay="animate-delay-3"
            isNumeric={true}
          />
          <KPICard
            title="Peak Enquiry Day"
            value={kpis.peakDay}
            subtitle={`${kpis.peakDayCount} enquiries on this day`}
            icon={CalendarDays}
            accentClass="text-kia-red"
            ariaLabel="Day with the most enquiries"
            animDelay="animate-delay-4"
          />
        </div>
      </section>

      {/* ═══════════════════════════════════════
          Charts Row: Trend + Customer Type Donut
         ═══════════════════════════════════════ */}
      <section aria-label="Enquiry Visualizations" className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
        {/* ── Trend Area Chart (2/3 width) ── */}
        <div
          className="lg:col-span-2 p-6 rounded-xl glass-panel border border-kia-border shadow-lg"
          role="img"
          aria-label="Area chart showing enquiry trend over time"
        >
          <div className="flex items-center justify-between mb-5">
            <div>
              <h4 className="text-lg font-bold text-[var(--color-kia-text)] section-heading">Enquiry Trend</h4>
              <p className="text-xs text-kia-muted" id="trend-chart-desc">
                Volume of incoming enquiries grouped by date ({trendData.length} data points)
              </p>
            </div>
          </div>

          <div className="h-[380px] w-full" aria-describedby="trend-chart-desc">
            {trendData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-kia-muted">
                <p className="text-sm">No date data available for trend chart</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={trendData}
                  margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
                >
                  <defs>
                    <linearGradient id="areaGradEnq" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#232733" vertical={false} />
                  <XAxis
                    dataKey="period"
                    stroke="var(--color-kia-muted)"
                    fontSize={10}
                    tickLine={false}
                    interval="preserveStartEnd"
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
                  <Tooltip content={<ChartTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="count"
                    name="Enquiries"
                    stroke="#3b82f6"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#areaGradEnq)"
                    dot={{ fill: '#3b82f6', r: 3, strokeWidth: 2, stroke: '#151720' }}
                    activeDot={{ r: 6, fill: "#3b82f6", stroke: "white", strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* ── Customer Type Donut Chart (1/3 width) ── */}
        <div
          className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg flex flex-col"
          role="img"
          aria-label="Donut chart comparing Individual versus Corporate enquiries"
        >
          <div className="mb-4">
            <h4 className="text-lg font-bold text-[var(--color-kia-text)] section-heading">Customer Type</h4>
            <p className="text-xs text-kia-muted" id="donut-chart-desc">Individual vs. Corporate split</p>
          </div>

          <div className="flex-1 min-h-[260px] flex items-center justify-center" aria-describedby="donut-chart-desc">
            {typeBreakdown.length === 0 ? (
              <p className="text-sm text-kia-muted">No customer type data</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={typeBreakdown.map((d) => ({ name: d.type, value: d.count }))}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={100}
                    paddingAngle={4}
                    dataKey="value"
                    label={({ name, percent }) =>
                      `${name} (${(percent * 100).toFixed(1)}%)`
                    }
                    labelLine={{ stroke: "var(--color-kia-muted)", strokeWidth: 1 }}
                    animationBegin={200}
                    animationDuration={800}
                    animationEasing="ease-out"
                  >
                    {typeBreakdown.map((_, idx) => (
                      <Cell
                        key={`cell-${idx}`}
                        fill={DONUT_COLORS[idx % DONUT_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  {/* Center label showing total */}
                  <Pie
                    data={[{ value: 1 }]}
                    cx="50%"
                    cy="50%"
                    innerRadius={0}
                    outerRadius={0}
                    dataKey="value"
                    fill="none"
                    stroke="none"
                    label={<DonutCenterLabel total={kpis.total} />}
                    isAnimationActive={false}
                  >
                    <Cell fill="none" />
                  </Pie>
                  <Tooltip
                    formatter={(value) => [value.toLocaleString(), "Enquiries"]}
                    contentStyle={{
                      backgroundColor: "var(--color-kia-card)",
                      borderColor: "var(--color-kia-border)",
                      color: "var(--color-kia-text)",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Legend below donut */}
          {typeBreakdown.length > 0 && (
            <div className="mt-3 space-y-2">
              {typeBreakdown.map((item, idx) => (
                <div key={item.type} className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-2">
                    <span
                      className="w-3 h-3 rounded-full inline-block"
                      style={{ backgroundColor: DONUT_COLORS[idx % DONUT_COLORS.length] }}
                      aria-hidden="true"
                    />
                    <span className="text-[var(--color-kia-text)] font-medium">{item.type}</span>
                  </span>
                  <span className="text-kia-muted font-semibold">
                    {item.count.toLocaleString()} ({item.percentage}%)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      {/* ═══════════════════════════════════════
          Interactive Data Table (client-side)
         ═══════════════════════════════════════ */}
      <section
        className="p-6 rounded-xl glass-panel border border-kia-border shadow-lg animate-fade-in"
        aria-label="Enquiry data table"
      >
        {/* Table Header: Title + Controls */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
          <div>
            <h4 className="text-lg font-bold text-[var(--color-kia-text)] flex items-center gap-2 section-heading">
              <BarChart3 size={20} className="text-kia-red" aria-hidden="true" />
              Raw Enquiry Data
            </h4>
            <p className="text-xs text-kia-muted" aria-live="polite">
              {processedTable.totalRecords.toLocaleString()} records
              {debouncedSearch ? ` matching "${debouncedSearch}"` : ""}
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Search Input */}
            <div className="relative">
              <Search
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-kia-muted"
                aria-hidden="true"
              />
              <input
                ref={searchInputRef}
                type="search"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search customer, model, city..."
                className="pl-9 pr-4 py-2 text-xs bg-[var(--color-kia-dark)] border border-kia-border rounded-lg text-[var(--color-kia-text)] placeholder:text-kia-muted/60 focus:outline-none focus:ring-2 focus:ring-kia-red/50 focus:border-kia-red w-64 transition-all"
                aria-label="Search enquiry records"
              />
            </div>

            {/* Customer Type Filter */}
            <select
              value={customerTypeFilter}
              onChange={(e) => {
                setCustomerTypeFilter(e.target.value);
                setPage(1);
              }}
              className="bg-[var(--color-kia-dark)] border border-kia-border rounded-lg px-3 py-2 text-xs text-[var(--color-kia-text)] focus:outline-none focus:ring-2 focus:ring-kia-red/50 focus:border-kia-red cursor-pointer"
              aria-label="Filter by customer type"
            >
              <option value="">All Types</option>
              <option value="Individual">Individual</option>
              <option value="Corporate">Corporate</option>
            </select>

            {/* Page Size Selector */}
            <select
              value={pageSize}
              onChange={(e) => handlePageSizeChange(Number(e.target.value))}
              className="bg-[var(--color-kia-dark)] border border-kia-border rounded-lg px-3 py-2 text-xs text-[var(--color-kia-text)] focus:outline-none focus:ring-2 focus:ring-kia-red/50 focus:border-kia-red cursor-pointer"
              aria-label="Rows per page"
            >
              <option value={15}>15 / page</option>
              <option value={25}>25 / page</option>
              <option value={50}>50 / page</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse" role="table" aria-label="Enquiry records">
            <thead className="sticky top-0 bg-[var(--color-kia-card)] z-10">
              <tr className="border-b border-kia-border text-xs font-semibold text-kia-muted uppercase tracking-wider">
                {tableColumns.map((col) => (
                  <SortableHeader
                    key={col.key}
                    label={col.label}
                    column={col.key}
                    currentSort={sortBy}
                    currentOrder={sortOrder}
                    onSort={handleSort}
                  />
                ))}
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-kia-border">
              {processedTable.data.length === 0 ? (
                <tr>
                  <td colSpan={tableColumns.length} className="py-16 text-center text-kia-muted">
                    <div className="flex flex-col items-center">
                      <Search size={32} className="mb-3 text-kia-muted/40" />
                      <p className="text-sm font-medium text-[var(--color-kia-text)]">No records found</p>
                      <p className="text-xs mt-1">Try adjusting your search or filter criteria.</p>
                    </div>
                  </td>
                </tr>
              ) : (
                processedTable.data.map((row, idx) => (
                  <tr
                    key={idx}
                    className="hover:bg-white/[0.02] transition-colors table-row-animate"
                    style={{ animationDelay: `${idx * 15}ms` }}
                    role="row"
                  >
                    {tableColumns.map((col) => (
                      <td
                        key={col.key}
                        className={`py-2.5 px-4 text-xs whitespace-nowrap ${
                          col.key === "Customer Type"
                            ? row[col.key] === "Corporate"
                              ? "text-kia-orange font-semibold"
                              : "text-kia-blue font-semibold"
                            : col.key === "Enquiry Status"
                            ? "text-kia-green"
                            : "text-[var(--color-kia-text)]"
                        }`}
                      >
                        {col.key === "Enquiry Date"
                          ? String(row[col.key] ?? "—").slice(0, 16)
                          : (row[col.key] ?? "—")}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        {processedTable.totalPages > 1 && (
          <nav
            className="flex items-center justify-between mt-5 pt-4 border-t border-kia-border"
            aria-label="Table pagination"
          >
            <p className="text-xs text-kia-muted">
              Page <strong className="text-[var(--color-kia-text)]">{processedTable.page}</strong> of{" "}
              <strong className="text-[var(--color-kia-text)]">{processedTable.totalPages}</strong>
              <span className="hidden sm:inline ml-2">
                ({processedTable.totalRecords.toLocaleString()} total records)
              </span>
            </p>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={processedTable.page <= 1}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-kia-border text-kia-muted hover:text-[var(--color-kia-text)] hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all focus:outline-none focus:ring-2 focus:ring-kia-red"
                aria-label="Previous page"
              >
                <ChevronLeft size={14} />
                <span className="hidden sm:inline">Previous</span>
              </button>

              <button
                onClick={() => setPage((p) => Math.min(processedTable.totalPages, p + 1))}
                disabled={processedTable.page >= processedTable.totalPages}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-semibold rounded-lg border border-kia-border text-kia-muted hover:text-[var(--color-kia-text)] hover:bg-white/5 disabled:opacity-30 disabled:cursor-not-allowed transition-all focus:outline-none focus:ring-2 focus:ring-kia-red"
                aria-label="Next page"
              >
                <span className="hidden sm:inline">Next</span>
                <ChevronRight size={14} />
              </button>
            </div>
          </nav>
        )}
      </section>
    </div>
  );
}
