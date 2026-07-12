// Data Processing Utilities for the CRM Analytics Dashboard

// Parse date strings helper
export const parseDate = (dateStr) => {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? null : d;
};

// Check if a row falls in a date range
export const isWithinDateRange = (rowDateStr, startDate, endDate) => {
  if (!rowDateStr) return false;
  const rowDate = parseDate(rowDateStr);
  if (!rowDate) return false;
  
  if (startDate) {
    const sDate = new Date(startDate);
    sDate.setHours(0,0,0,0);
    if (rowDate < sDate) return false;
  }
  if (endDate) {
    const eDate = new Date(endDate);
    eDate.setHours(23,59,59,999);
    if (rowDate > eDate) return false;
  }
  return true;
};

// Apply global filters to dataset
export const filterData = (data, filters) => {
  return data.filter(row => {
    // 1. Date Range Filter
    const enqDateStr = row["Enquiry Date"] || row["enquiry date"];
    if (filters.startDate || filters.endDate) {
      if (!isWithinDateRange(enqDateStr, filters.startDate, filters.endDate)) {
        return false;
      }
    }
    
    // 2. Model Filter
    const model = (row["Model"] || row["model"] || "").toString().trim().toUpperCase();
    if (filters.model && filters.model !== "ALL") {
      if (model !== filters.model.toUpperCase()) return false;
    }
    
    // 3. Consultant Filter
    const consultant = (row["Consultant Name"] || row["consultant name"] || "").toString().trim().toUpperCase();
    if (filters.consultant && filters.consultant !== "ALL") {
      if (consultant !== filters.consultant.toUpperCase()) return false;
    }
    
    // 4. Source Filter
    const source = (row["Source"] || row["source"] || "").toString().trim().toUpperCase();
    if (filters.source && filters.source !== "ALL") {
      if (source !== filters.source.toUpperCase()) return false;
    }
    
    // 5. City/State Filter
    const city = (row["City"] || row["city"] || "").toString().trim().toUpperCase();
    const state = (row["State"] || row["state"] || "").toString().trim().toUpperCase();
    if (filters.cityState && filters.cityState !== "ALL") {
      const matchKey = `${city} (${state})`;
      const cityOnly = city;
      if (filters.cityState !== matchKey && filters.cityState !== cityOnly) return false;
    }
    
    // 6. Lead Type Filter
    const type = (row["Type"] || row["type"] || row["Customer Type"] || "").toString().trim().toUpperCase();
    if (filters.leadType && filters.leadType !== "ALL") {
      // Check both lead tier (Hot/Warm/Cold) and Customer Type if columns drift
      const rowType = (row["Type"] || "").toString().trim().toUpperCase();
      if (rowType !== filters.leadType.toUpperCase()) return false;
    }
    
    return true;
  });
};

// Extractor helpers for filter dropdowns
export const getUniqueValues = (data, key) => {
  const values = new Set();
  const seenUpper = new Set();
  data.forEach(row => {
    const val = row[key];
    if (val !== undefined && val !== null && val !== "") {
      const trimmed = val.toString().trim();
      const upper = trimmed.toUpperCase();
      if (!seenUpper.has(upper)) {
        seenUpper.add(upper);
        values.add(trimmed);
      }
    }
  });
  return ["ALL", ...Array.from(values).sort((a, b) => a.localeCompare(b))];
};

// Special extractor for City (State)
export const getCityStateOptions = (data) => {
  const values = new Set();
  const seenUpper = new Set();
  data.forEach(row => {
    const city = (row["City"] || row["city"] || "").toString().trim();
    const state = (row["State"] || row["state"] || "").toString().trim();
    if (city) {
      const key = state ? `${city} (${state})` : city;
      const upper = key.toUpperCase();
      if (!seenUpper.has(upper)) {
        seenUpper.add(upper);
        values.add(key);
      }
    }
  });
  return ["ALL", ...Array.from(values).sort((a, b) => a.localeCompare(b))];
};

// Process row boolean flags helper
export const getRowFlags = (row) => {
  const tdDate = row["Test Drive Date"] || row["test drive date"] || row["Test drive date"];
  const tdStatus = (row["TD Status"] || row["td status"] || "").toString().trim().toLowerCase();
  const tdGivenStr = (row["No. of test drive given"] || row["no. of test drive given"] || "0").toString();
  const tdGiven = parseFloat(tdGivenStr) || 0;
  
  const isTD = !!tdDate || tdStatus === "done" || tdGiven > 0;
  
  const bookingDate = row["Booking Date"] || row["booking date"];
  const isBooking = !!bookingDate;
  
  const retailDate = row["Retail date"] || row["retail date"] || row["Delivery Date"] || row["delivery date"];
  const status = (row["Enquiry Status"] || row["enquiry status"] || "").toString().trim().toLowerCase();
  const isRetail = !!retailDate || status === "retail";
  
  const agingStr = (row["enquiry aging days"] || row["enquiry aging days"] || "0").toString();
  const agingDays = parseInt(agingStr, 10) || 0;
  
  const followupStr = (row["Followup Count"] || row["followup count"] || "0").toString();
  const followupCount = parseInt(followupStr, 10) || 0;
  
  const expectedPriceStr = (row["Expected Price"] || row["expected price"] || "0").toString().replace(/[^0-9.]/g, '');
  const expectedPrice = parseFloat(expectedPriceStr) || 0;
  
  return { isTD, isBooking, isRetail, agingDays, followupCount, expectedPrice };
};

// Calculate core KPIs
export const calculateKPIs = (data) => {
  const total = data.length;
  if (total === 0) {
    return { total: 0, tdRate: 0, retailRate: 0, avgAging: 0, bookings: 0, retails: 0 };
  }
  
  let tdCount = 0;
  let bookingCount = 0;
  let retailCount = 0;
  let totalAging = 0;
  
  data.forEach(row => {
    const { isTD, isBooking, isRetail, agingDays } = getRowFlags(row);
    if (isTD) tdCount++;
    if (isBooking) bookingCount++;
    if (isRetail) retailCount++;
    totalAging += agingDays;
  });
  
  return {
    total,
    tdRate: (tdCount / total) * 100,
    retailRate: (retailCount / total) * 100,
    avgAging: totalAging / total,
    bookings: bookingCount,
    retails: retailCount
  };
};

// Aggregate trends over time (Grouped by date format e.g., Month or Date)
export const getEnquiryTrend = (data) => {
  const dailyData = {};
  
  data.forEach(row => {
    const rawDateStr = row["Enquiry Date"] || row["enquiry date"];
    if (!rawDateStr) return;
    
    // Extract date prefix YYYY-MM-DD
    const dateKey = rawDateStr.split(' ')[0]; 
    if (!dateKey) return;
    
    const { isRetail } = getRowFlags(row);
    
    if (!dailyData[dateKey]) {
      dailyData[dateKey] = { date: dateKey, enquiries: 0, retails: 0 };
    }
    
    dailyData[dateKey].enquiries++;
    if (isRetail) dailyData[dateKey].retails++;
  });
  
  // Sort chronologically
  return Object.values(dailyData).sort((a, b) => new Date(a.date) - new Date(b.date));
};

// Lead Funnel calculations
export const getFunnelData = (data) => {
  const total = data.length;
  if (total === 0) return [];
  
  let tdScheduled = 0;
  let tdCompleted = 0;
  let converted = 0;
  let lost = 0;
  
  data.forEach(row => {
    const { isTD, isBooking, isRetail } = getRowFlags(row);
    const status = (row["Enquiry Status"] || "").toString().trim().toLowerCase();
    const lostReason = (row["lost reason"] || row["Lost Reason"] || "").toString().trim();
    const lostDueTo = (row["lost due to"] || "").toString().trim();
    
    const tdStatus = (row["TD Status"] || "").toString().trim().toLowerCase();
    const tdDate = row["Test Drive Date"] || row["test drive date"];
    
    if (tdDate || tdStatus === "scheduled" || tdStatus === "done" || tdStatus === "no-show" || tdStatus === "cancelled") {
      tdScheduled++;
    }
    if (isTD) {
      tdCompleted++;
    }
    if (isRetail || isBooking) {
      converted++;
    } else if (lostReason || lostDueTo || status.includes("cancel") || status.includes("lost")) {
      lost++;
    }
  });
  
  return [
    { name: "Enquiry", value: total, percentage: 100 },
    { name: "TD Scheduled", value: tdScheduled, percentage: total > 0 ? (tdScheduled / total) * 100 : 0 },
    { name: "TD Completed", value: tdCompleted, percentage: total > 0 ? (tdCompleted / total) * 100 : 0 },
    { name: "Converted (Booked/Retail)", value: converted, percentage: total > 0 ? (converted / total) * 100 : 0 },
    { name: "Lost / Dropped Off", value: lost, percentage: total > 0 ? (lost / total) * 100 : 0 }
  ];
};

// Group by frequency helper
export const groupAndCount = (data, key, formatFn = (x) => x || "UNKNOWN") => {
  const counts = {};
  data.forEach(row => {
    const rawVal = row[key];
    const val = formatFn(rawVal);
    counts[val] = (counts[val] || 0) + 1;
  });
  
  return Object.entries(counts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
};

// Group by Consultant Performance
export const getConsultantPerformance = (data) => {
  const consultants = {};
  
  data.forEach(row => {
    const rawName = row["Consultant Name"] || row["consultant name"];
    const name = rawName ? rawName.toString().trim().toUpperCase() : "UNKNOWN";
    if (name === "UNKNOWN") return;
    
    const { isRetail, followupCount, agingDays } = getRowFlags(row);
    
    if (!consultants[name]) {
      consultants[name] = {
        name,
        leads: 0,
        retails: 0,
        totalFollowup: 0,
        totalAging: 0
      };
    }
    
    consultants[name].leads++;
    if (isRetail) consultants[name].retails++;
    consultants[name].totalFollowup += followupCount;
    consultants[name].totalAging += agingDays;
  });
  
  return Object.values(consultants).map(c => {
    const conversion = c.leads > 0 ? (c.retails / c.leads) * 100 : 0;
    const avgFollowup = c.leads > 0 ? c.totalFollowup / c.leads : 0;
    const avgAging = c.leads > 0 ? c.totalAging / c.leads : 0;
    
    // Efficiency flag: high follow-ups but low conversion
    // Define gap as: avg followups > 4.0 AND conversion rate < 8%
    const efficiencyGap = avgFollowup >= 4.0 && conversion < 8.0;
    
    return {
      name: c.name,
      leads: c.leads,
      retails: c.retails,
      conversion: parseFloat(conversion.toFixed(1)),
      avgFollowup: parseFloat(avgFollowup.toFixed(1)),
      avgAging: parseFloat(avgAging.toFixed(1)),
      efficiencyGap
    };
  }).sort((a, b) => b.retails - a.retails); // Rank by retails
};

// Source Performance
export const getSourcePerformance = (data) => {
  const sources = {};
  
  data.forEach(row => {
    const source = (row["Source"] || row["source"] || "UNKNOWN").toString().trim();
    const subSource = (row["Sub-source"] || row["sub-source"] || "UNKNOWN").toString().trim();
    const { isRetail, isTD } = getRowFlags(row);
    
    const key = `${source} - ${subSource}`;
    
    if (!sources[key]) {
      sources[key] = {
        key,
        source,
        subSource,
        leads: 0,
        tds: 0,
        retails: 0
      };
    }
    
    sources[key].leads++;
    if (isTD) sources[key].tds++;
    if (isRetail) sources[key].retails++;
  });
  
  return Object.values(sources).map(s => {
    return {
      ...s,
      tdRate: s.leads > 0 ? parseFloat(((s.tds / s.leads) * 100).toFixed(1)) : 0,
      conversionRate: s.leads > 0 ? parseFloat(((s.retails / s.leads) * 100).toFixed(1)) : 0
    };
  }).sort((a, b) => b.leads - a.leads);
};

// Best-performing source per Model
export const getBestSourcePerModel = (data) => {
  const modelSourcePairs = {};
  
  data.forEach(row => {
    const model = (row["Model"] || "UNKNOWN").toString().trim().toUpperCase();
    const source = (row["Source"] || "UNKNOWN").toString().trim();
    if (model === "UNKNOWN") return;
    
    const { isRetail } = getRowFlags(row);
    
    const key = `${model}::${source}`;
    if (!modelSourcePairs[key]) {
      modelSourcePairs[key] = { model, source, leads: 0, retails: 0 };
    }
    modelSourcePairs[key].leads++;
    if (isRetail) modelSourcePairs[key].retails++;
  });
  
  // Find highest conversion rate source for each model with at least 5 leads
  const models = {};
  Object.values(modelSourcePairs).forEach(pair => {
    const rate = pair.leads > 0 ? (pair.retails / pair.leads) * 100 : 0;
    if (!models[pair.model]) {
      models[pair.model] = [];
    }
    models[pair.model].push({ source: pair.source, leads: pair.leads, retails: pair.retails, rate });
  });
  
  const bestSources = [];
  Object.entries(models).forEach(([model, sourcesList]) => {
    // filter to sources with > 2 leads or take max
    const valid = sourcesList.length > 0 ? sourcesList : [];
    if (valid.length === 0) return;
    
    valid.sort((a, b) => b.rate - a.rate || b.leads - a.leads);
    const best = valid[0];
    bestSources.push({
      model,
      bestSource: best.source,
      conversionRate: parseFloat(best.rate.toFixed(1)),
      leads: best.leads,
      retails: best.retails
    });
  });
  
  return bestSources.sort((a, b) => b.leads - a.leads);
};

// Campaign Name performance
export const getCampaignPerformance = (data) => {
  const campaigns = {};
  data.forEach(row => {
    const campaign = (row["Campaign Name"] || row["campaign name"] || "No Campaign/Organic").toString().trim();
    const { isRetail } = getRowFlags(row);
    
    if (!campaigns[campaign]) {
      campaigns[campaign] = { name: campaign, leads: 0, retails: 0 };
    }
    campaigns[campaign].leads++;
    if (isRetail) campaigns[campaign].retails++;
  });
  
  return Object.values(campaigns).map(c => {
    const conversionRate = c.leads > 0 ? parseFloat(((c.retails / c.leads) * 100).toFixed(1)) : 0;
    return { ...c, conversionRate };
  }).sort((a, b) => b.leads - a.leads).slice(0, 10); // Top 10 campaigns
};

// Model Performance Breakdown
export const getModelPerformance = (data) => {
  const models = {};
  data.forEach(row => {
    const model = (row["Model"] || "UNKNOWN").toString().trim().toUpperCase();
    const variant = (row["Variant"] || "UNKNOWN").toString().trim();
    const fuel = (row["Fuel type"] || row["Fuel Type"] || "UNKNOWN").toString().trim();
    const { isRetail, isTD } = getRowFlags(row);
    
    if (!models[model]) {
      models[model] = { name: model, leads: 0, tds: 0, retails: 0, variants: {}, fuelTypes: {} };
    }
    models[model].leads++;
    if (isTD) models[model].tds++;
    if (isRetail) models[model].retails++;
    
    if (variant && variant !== "UNKNOWN") {
      models[model].variants[variant] = (models[model].variants[variant] || 0) + 1;
    }
    if (fuel && fuel !== "UNKNOWN") {
      models[model].fuelTypes[fuel] = (models[model].fuelTypes[fuel] || 0) + 1;
    }
  });
  
  return Object.values(models).map(m => {
    const conversionRate = m.leads > 0 ? parseFloat(((m.retails / m.leads) * 100).toFixed(1)) : 0;
    const tdRate = m.leads > 0 ? parseFloat(((m.tds / m.leads) * 100).toFixed(1)) : 0;
    
    // Sort variant list
    const topVariants = Object.entries(m.variants)
      .sort((a,b) => b[1] - a[1])
      .slice(0, 3)
      .map(([name]) => name)
      .join(", ");
      
    // Sort fuel list
    const topFuel = Object.entries(m.fuelTypes)
      .sort((a,b) => b[1] - a[1])
      .map(([name]) => name)
      .join("/");
      
    return {
      model: m.name,
      leads: m.leads,
      tds: m.tds,
      retails: m.retails,
      tdRate,
      conversionRate,
      topVariants: topVariants || "N/A",
      topFuel: topFuel || "N/A"
    };
  }).sort((a, b) => b.leads - a.leads);
};

// Expected Price distribution by Model
export const getPriceDistribution = (data) => {
  const modelPrices = {};
  data.forEach(row => {
    const model = (row["Model"] || "UNKNOWN").toString().trim().toUpperCase();
    if (model === "UNKNOWN") return;
    
    const { expectedPrice } = getRowFlags(row);
    if (expectedPrice <= 0) return; // filter out blank/0 prices
    
    if (!modelPrices[model]) {
      modelPrices[model] = [];
    }
    modelPrices[model].push(expectedPrice);
  });
  
  return Object.entries(modelPrices).map(([model, prices]) => {
    prices.sort((a,b) => a - b);
    const len = prices.length;
    const avg = prices.reduce((a,b) => a+b, 0) / len;
    const min = prices[0];
    const max = prices[len - 1];
    const median = prices[Math.floor(len / 2)];
    
    return {
      model,
      count: len,
      avg: parseFloat(avg.toFixed(0)),
      min,
      max,
      median
    };
  }).sort((a, b) => b.count - a.count);
};

// OEM Model Cross-shopping Competitors
export const getOEMComparison = (data) => {
  const competitors = {};
  data.forEach(row => {
    const oemModel = (row["OEM Model"] || row["oem model"] || "").toString().trim();
    if (!oemModel) return;
    
    const key = oemModel.toUpperCase();
    if (!competitors[key]) {
      competitors[key] = { name: oemModel, count: 0 };
    }
    competitors[key].count++;
  });
  
  return Object.values(competitors).sort((a,b) => b.count - a.count).slice(0, 10);
};

// Present Car Trade-in Conversion Rate Split
export const getPresentCarSplit = (data) => {
  let hasCarCount = 0;
  let hasCarRetails = 0;
  let noCarCount = 0;
  let noCarRetails = 0;
  
  data.forEach(row => {
    const hasCar = (row["Present Car(Y/N)"] || row["Present Car (Y/N)"] || "N").toString().trim().toUpperCase() === "Y";
    const { isRetail } = getRowFlags(row);
    
    if (hasCar) {
      hasCarCount++;
      if (isRetail) hasCarRetails++;
    } else {
      noCarCount++;
      if (isRetail) noCarRetails++;
    }
  });
  
  const hasCarRate = hasCarCount > 0 ? (hasCarRetails / hasCarCount) * 100 : 0;
  const noCarRate = noCarCount > 0 ? (noCarRetails / noCarCount) * 100 : 0;
  
  return [
    { name: "Trade-in (Has Car)", count: hasCarCount, retails: hasCarRetails, conversionRate: parseFloat(hasCarRate.toFixed(1)) },
    { name: "Fresh Purchase (No Car)", count: noCarCount, retails: noCarRetails, conversionRate: parseFloat(noCarRate.toFixed(1)) }
  ];
};

// Geographic summary
export const getGeographicPerformance = (data) => {
  const regions = {};
  
  data.forEach(row => {
    const city = (row["City"] || "UNKNOWN").toString().trim().toUpperCase();
    const state = (row["State"] || "UNKNOWN").toString().trim().toUpperCase();
    const { isRetail } = getRowFlags(row);
    
    const key = `${city} (${state})`;
    
    if (!regions[key]) {
      regions[key] = { key, city, state, leads: 0, retails: 0 };
    }
    regions[key].leads++;
    if (isRetail) regions[key].retails++;
  });
  
  return Object.values(regions).map(r => {
    const conversionRate = r.leads > 0 ? parseFloat(((r.retails / r.leads) * 100).toFixed(1)) : 0;
    return { ...r, conversionRate };
  }).sort((a,b) => b.leads - a.leads);
};

// Funnel Velocity - Aging Days Distribution
export const getAgingDistribution = (data) => {
  const buckets = {
    "0-7 days": { enquiries: 0, retails: 0 },
    "8-15 days": { enquiries: 0, retails: 0 },
    "16-30 days": { enquiries: 0, retails: 0 },
    "31-45 days": { enquiries: 0, retails: 0 },
    "46-60 days": { enquiries: 0, retails: 0 },
    "61+ days": { enquiries: 0, retails: 0 }
  };
  
  data.forEach(row => {
    const { agingDays, isRetail } = getRowFlags(row);
    
    let bucketName = "61+ days";
    if (agingDays <= 7) bucketName = "0-7 days";
    else if (agingDays <= 15) bucketName = "8-15 days";
    else if (agingDays <= 30) bucketName = "16-30 days";
    else if (agingDays <= 45) bucketName = "31-45 days";
    else if (agingDays <= 60) bucketName = "46-60 days";
    
    buckets[bucketName].enquiries++;
    if (isRetail) buckets[bucketName].retails++;
  });
  
  return Object.entries(buckets).map(([name, info]) => {
    const conversionRate = info.enquiries > 0 ? parseFloat(((info.retails / info.enquiries) * 100).toFixed(1)) : 0;
    return {
      name,
      enquiries: info.enquiries,
      retails: info.retails,
      conversionRate
    };
  });
};

// Followup Count vs Conversion Rate Correlation
export const getFollowupCorrelation = (data) => {
  const buckets = {
    "0": { enquiries: 0, retails: 0 },
    "1": { enquiries: 0, retails: 0 },
    "2": { enquiries: 0, retails: 0 },
    "3-4": { enquiries: 0, retails: 0 },
    "5-6": { enquiries: 0, retails: 0 },
    "7-10": { enquiries: 0, retails: 0 },
    "11+": { enquiries: 0, retails: 0 }
  };
  
  data.forEach(row => {
    const { followupCount, isRetail } = getRowFlags(row);
    
    let bucketName = "11+";
    if (followupCount === 0) bucketName = "0";
    else if (followupCount === 1) bucketName = "1";
    else if (followupCount === 2) bucketName = "2";
    else if (followupCount <= 4) bucketName = "3-4";
    else if (followupCount <= 6) bucketName = "5-6";
    else if (followupCount <= 10) bucketName = "7-10";
    
    buckets[bucketName].enquiries++;
    if (isRetail) buckets[bucketName].retails++;
  });
  
  return Object.entries(buckets).map(([name, info]) => {
    const conversionRate = info.enquiries > 0 ? parseFloat(((info.retails / info.enquiries) * 100).toFixed(1)) : 0;
    return {
      name,
      enquiries: info.enquiries,
      retails: info.retails,
      conversionRate
    };
  });
};

// Customer Type conversion comparison (new vs repeat or individual vs corporate)
export const getCustomerTypeComparison = (data) => {
  const types = {};
  
  data.forEach(row => {
    const customerType = (row["Customer Type"] || row["customer type"] || "Individual").toString().trim();
    const { isRetail } = getRowFlags(row);
    
    if (!types[customerType]) {
      types[customerType] = { name: customerType, enquiries: 0, retails: 0 };
    }
    types[customerType].enquiries++;
    if (isRetail) types[customerType].retails++;
  });
  
  return Object.values(types).map(t => {
    const conversionRate = t.enquiries > 0 ? parseFloat(((t.retails / t.enquiries) * 100).toFixed(1)) : 0;
    return { ...t, conversionRate };
  });
};

// Lost reasons grouped by Model
export const getLostReasonsByModel = (data) => {
  const mapping = {};
  
  data.forEach(row => {
    const model = (row["Model"] || "UNKNOWN").toString().trim().toUpperCase();
    const lostReason = (row["lost reason"] || row["Lost Reason"] || row["lost due to"] || "").toString().trim();
    if (!lostReason || model === "UNKNOWN") return;
    
    const key = `${model}::${lostReason}`;
    mapping[key] = (mapping[key] || 0) + 1;
  });
  
  const result = {};
  Object.entries(mapping).forEach(([key, count]) => {
    const [model, reason] = key.split('::');
    if (!result[model]) {
      result[model] = [];
    }
    result[model].push({ reason, count });
  });
  
  // Sort and select top reasons per model
  const sortedResult = {};
  Object.entries(result).forEach(([model, list]) => {
    list.sort((a,b) => b.count - a.count);
    sortedResult[model] = list.slice(0, 5); // top 5 lost reasons
  });
  
  return sortedResult;
};
