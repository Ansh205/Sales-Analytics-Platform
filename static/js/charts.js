/**
 * Executive & Page Analytics ECharts Visualization Module
 * Sales Analytics Platform (Phase 6.4 & 6.5)
 */

// Global ECharts instance map
const chartInstances = {};

// Month names lookup
const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Currency formatter for tooltips & axis labels
function formatChartCurrency(val) {
  if (val === null || val === undefined || isNaN(val)) return '$0';
  const num = Number(val);
  if (Math.abs(num) >= 1000000) {
    return `$${(num / 1000000).toFixed(2)}M`;
  }
  if (Math.abs(num) >= 1000) {
    return `$${(num / 1000).toFixed(1)}K`;
  }
  return `$${num.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
}

// Get or initialize ECharts instance
function getOrCreateChart(elementId) {
  const dom = document.getElementById(elementId);
  if (!dom) return null;

  let chart = echarts.getInstanceByDom(dom);
  if (!chart) {
    chart = echarts.init(dom);
  }
  return chart;
}

// Show empty state inside chart container
function showChartEmpty(chart, message = 'No data available for the selected filters.') {
  if (!chart) return;
  chart.clear();
  chart.setOption({
    title: {
      text: message,
      left: 'center',
      top: 'middle',
      textStyle: {
        color: '#64748b',
        fontSize: 14,
        fontWeight: 500
      }
    }
  });
}

// Window resize handler for all active charts
window.addEventListener('resize', () => {
  Object.values(chartInstances).forEach(chart => {
    if (chart) {
      chart.resize();
    }
  });
});

/**
 * 1. Render Sales & Profit Trend (Line Chart)
 */
function renderSalesTrend(data, elementId = 'salesTrendChart') {
  const chart = getOrCreateChart(elementId);
  if (!chart) return;
  chartInstances[elementId] = chart;

  if (!data || !Array.isArray(data) || data.length === 0) {
    showChartEmpty(chart);
    return;
  }

  chart.clear();

  const uniqueYears = new Set(data.map(d => d.year)).size;
  const categories = data.map(d => {
    const monthName = MONTH_NAMES[(d.month - 1) % 12] || `M${d.month}`;
    return uniqueYears > 1 ? `${monthName} ${d.year}` : monthName;
  });

  const salesSeries = data.map(d => Number(d.sales || 0));
  const profitSeries = data.map(d => Number(d.profit || 0));

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#ffffff',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 12 },
      formatter: function (params) {
        let tooltipText = `<div style="font-weight:600;margin-bottom:4px;">${params[0].name}</div>`;
        params.forEach(item => {
          tooltipText += `
            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;font-size:12px;">
              <span>${item.marker} ${item.seriesName}</span>
              <span style="font-weight:600;">${formatChartCurrency(item.value)}</span>
            </div>`;
        });
        return tooltipText;
      }
    },
    legend: {
      data: ['Sales', 'Profit'],
      top: 0,
      right: 10,
      textStyle: { color: '#64748b', fontSize: 12 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '40px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: categories,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#64748b', fontSize: 11, rotate: categories.length > 15 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (val) => formatChartCurrency(val)
      }
    },
    series: [
      {
        name: 'Sales',
        type: 'line',
        smooth: true,
        showSymbol: data.length < 20,
        symbolSize: 6,
        lineStyle: { width: 3, color: '#2563eb' },
        itemStyle: { color: '#2563eb' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(37, 99, 235, 0.25)' },
            { offset: 1, color: 'rgba(37, 99, 235, 0.01)' }
          ])
        },
        data: salesSeries
      },
      {
        name: 'Profit',
        type: 'line',
        smooth: true,
        showSymbol: data.length < 20,
        symbolSize: 6,
        lineStyle: { width: 3, color: '#10b981' },
        itemStyle: { color: '#10b981' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.2)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0.01)' }
          ])
        },
        data: profitSeries
      }
    ]
  };

  chart.setOption(option);
}

/**
 * 2. Render Sales by Region (Horizontal Bar Chart)
 */
function renderRegionChart(data, elementId = 'regionChart') {
  const chart = getOrCreateChart(elementId);
  if (!chart) return;
  chartInstances[elementId] = chart;

  if (!data || !Array.isArray(data) || data.length === 0) {
    showChartEmpty(chart);
    return;
  }

  chart.clear();

  const sortedData = [...data].sort((a, b) => Number(a.sales) - Number(b.sales));
  const regions = sortedData.map(d => d.region);
  const sales = sortedData.map(d => Number(d.sales || 0));

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#ffffff',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 12 },
      formatter: function (params) {
        const item = params[0];
        return `
          <div style="font-weight:600;margin-bottom:4px;">${item.name} Region</div>
          <div style="font-size:12px;">Sales: <strong>${formatChartCurrency(item.value)}</strong></div>`;
      }
    },
    grid: {
      left: '3%',
      right: '6%',
      bottom: '3%',
      top: '15px',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (val) => formatChartCurrency(val)
      }
    },
    yAxis: {
      type: 'category',
      data: regions,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#0f172a', fontSize: 12, fontWeight: 500 }
    },
    series: [
      {
        name: 'Sales',
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: '#2563eb',
          borderRadius: [0, 4, 4, 0]
        },
        data: sales
      }
    ]
  };

  chart.setOption(option);
}

/**
 * 3. Render Top Products (Horizontal Bar Chart)
 */
function renderProductChart(data, elementId = 'productChart') {
  const chart = getOrCreateChart(elementId);
  if (!chart) return;
  chartInstances[elementId] = chart;

  if (!data || !Array.isArray(data) || data.length === 0) {
    showChartEmpty(chart);
    return;
  }

  chart.clear();

  const sortedData = [...data].reverse();
  const productFullNames = sortedData.map(d => d.product_name || 'Unknown Product');
  const sales = sortedData.map(d => Number(d.sales || 0));

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#ffffff',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 12 },
      formatter: function (params) {
        const index = params[0].dataIndex;
        const fullName = productFullNames[index];
        const val = params[0].value;
        return `
          <div style="font-weight:600;margin-bottom:4px;max-width:300px;white-space:normal;">${fullName}</div>
          <div style="font-size:12px;">Total Sales: <strong>${formatChartCurrency(val)}</strong></div>`;
      }
    },
    grid: {
      left: '3%',
      right: '6%',
      bottom: '3%',
      top: '15px',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (val) => formatChartCurrency(val)
      }
    },
    yAxis: {
      type: 'category',
      data: productFullNames,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: {
        color: '#0f172a',
        fontSize: 11,
        formatter: function (name) {
          return name.length > 20 ? name.substring(0, 18) + '...' : name;
        }
      }
    },
    series: [
      {
        name: 'Sales',
        type: 'bar',
        barWidth: '55%',
        itemStyle: {
          color: '#06b6d4',
          borderRadius: [0, 4, 4, 0]
        },
        data: sales
      }
    ]
  };

  chart.setOption(option);
}

/**
 * 4. Render Top Customers (Horizontal Bar Chart)
 */
function renderCustomerChart(data, elementId = 'customerChart') {
  const chart = getOrCreateChart(elementId);
  if (!chart) return;
  chartInstances[elementId] = chart;

  if (!data || !Array.isArray(data) || data.length === 0) {
    showChartEmpty(chart);
    return;
  }

  chart.clear();

  const sortedData = [...data].reverse();
  const customerNames = sortedData.map(d => d.customer_name || 'Unknown Customer');
  const sales = sortedData.map(d => Number(d.sales || 0));

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      backgroundColor: '#ffffff',
      borderColor: '#e2e8f0',
      borderWidth: 1,
      textStyle: { color: '#0f172a', fontSize: 12 },
      formatter: function (params) {
        const item = params[0];
        return `
          <div style="font-weight:600;margin-bottom:4px;">${item.name}</div>
          <div style="font-size:12px;">Total Purchases: <strong>${formatChartCurrency(item.value)}</strong></div>`;
      }
    },
    grid: {
      left: '3%',
      right: '6%',
      bottom: '3%',
      top: '15px',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#f1f5f9' } },
      axisLabel: {
        color: '#64748b',
        fontSize: 11,
        formatter: (val) => formatChartCurrency(val)
      }
    },
    yAxis: {
      type: 'category',
      data: customerNames,
      axisLine: { lineStyle: { color: '#e2e8f0' } },
      axisLabel: { color: '#0f172a', fontSize: 12, fontWeight: 500 }
    },
    series: [
      {
        name: 'Sales',
        type: 'bar',
        barWidth: '55%',
        itemStyle: {
          color: '#6366f1',
          borderRadius: [0, 4, 4, 0]
        },
        data: sales
      }
    ]
  };

  chart.setOption(option);
}
