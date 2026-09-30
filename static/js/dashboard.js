/**
 * Executive Dashboard Vanilla JavaScript Integration & Controller
 * Sales Analytics Platform (Phase 6.4)
 */

// Format currency values (e.g. $2.30M, $286.40K, or $1,234.56)
function formatCurrency(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return '$0.00';
  }
  const num = Number(value);
  if (Math.abs(num) >= 1000000) {
    return `$${(num / 1000000).toFixed(2)}M`;
  }
  if (Math.abs(num) >= 1000) {
    return `$${(num / 1000).toFixed(2)}K`;
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
}

// Format integer values with thousands separators (e.g. 5,009)
function formatNumber(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0';
  }
  return new Intl.NumberFormat('en-US').format(Number(value));
}

// Format percentage values (e.g. 12.46%)
function formatPercentage(value) {
  if (value === null || value === undefined || isNaN(value)) {
    return '0.00%';
  }
  return `${Number(value).toFixed(2)}%`;
}

// Read current select dropdown values
function getSelectedFilters() {
  const year = document.getElementById('yearFilter')?.value || '';
  const region = document.getElementById('regionFilter')?.value || '';
  const category = document.getElementById('categoryFilter')?.value || '';
  const segment = document.getElementById('segmentFilter')?.value || '';

  return { year, region, category, segment };
}

// Construct query string using URLSearchParams safely
function buildQueryString(filters) {
  if (!filters) return '';
  const params = new URLSearchParams();

  if (filters.year) params.append('year', filters.year);
  if (filters.region) params.append('region', filters.region);
  if (filters.category) params.append('category', filters.category);
  if (filters.segment) params.append('segment', filters.segment);

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}

// Update active filters badge text
function updateActiveFiltersIndicator(filters) {
  const badgeText = document.getElementById('activeFiltersText');
  if (!badgeText) return;

  if (!filters) {
    badgeText.textContent = 'None';
    return;
  }

  const activeParts = [];
  if (filters.year) activeParts.push(`Year: ${filters.year}`);
  if (filters.region) activeParts.push(`Region: ${filters.region}`);
  if (filters.category) activeParts.push(`Category: ${filters.category}`);
  if (filters.segment) activeParts.push(`Segment: ${filters.segment}`);

  if (activeParts.length === 0) {
    badgeText.textContent = 'None';
  } else {
    badgeText.textContent = activeParts.join(' | ');
  }
}

// Set loading skeleton state in KPI cards
function setLoadingState() {
  const errorBanner = document.getElementById('errorBanner');
  if (errorBanner) {
    errorBanner.classList.remove('visible');
  }

  const kpiIds = ['kpi-sales', 'kpi-profit', 'kpi-orders', 'kpi-customers', 'kpi-margin', 'kpi-return'];
  kpiIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.innerHTML = '<span class="skeleton skeleton-text"></span>';
    }
  });
}

// Display error state banner
function showErrorState(message) {
  const errorBanner = document.getElementById('errorBanner');
  const errorMessage = document.getElementById('errorMessage');
  if (errorMessage) {
    errorMessage.textContent = message || 'Unable to update dashboard data. Please check that the API server is running.';
  }
  if (errorBanner) {
    errorBanner.classList.add('visible');
  }

  const kpiIds = ['kpi-sales', 'kpi-profit', 'kpi-orders', 'kpi-customers', 'kpi-margin', 'kpi-return'];
  kpiIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = '—';
    }
  });
}

// Update 6 KPI card elements with API response data
function updateKPIs(data) {
  if (!data) return;

  document.getElementById('kpi-sales').textContent = formatCurrency(data.total_sales);
  document.getElementById('kpi-profit').textContent = formatCurrency(data.total_profit);
  document.getElementById('kpi-orders').textContent = formatNumber(data.total_orders);
  document.getElementById('kpi-customers').textContent = formatNumber(data.total_customers);
  document.getElementById('kpi-margin').textContent = formatPercentage(data.profit_margin);
  document.getElementById('kpi-return').textContent = formatPercentage(data.return_rate);
}

// Fetch single API endpoint safely returning JSON
async function fetchEndpoint(url) {
  const res = await fetch(url, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status} fetching ${url}`);
  }
  return await res.json();
}

// Fetch summary metrics and 4 chart payloads concurrently using Promise.all
async function loadDashboardData(filters = null) {
  setLoadingState();
  const queryString = buildQueryString(filters);

  const summaryUrl = `/api/summary${queryString}`;
  const monthlyUrl = `/api/sales/monthly${queryString}`;
  const regionUrl = `/api/sales/region${queryString}`;
  const productUrl = `/api/products/top${queryString ? queryString + '&limit=10' : '?limit=10'}`;
  const customerUrl = `/api/customers/top${queryString ? queryString + '&limit=10' : '?limit=10'}`;

  try {
    const [summaryData, monthlyData, regionData, productData, customerData] = await Promise.all([
      fetchEndpoint(summaryUrl),
      fetchEndpoint(monthlyUrl),
      fetchEndpoint(regionUrl),
      fetchEndpoint(productUrl),
      fetchEndpoint(customerUrl)
    ]);

    // 1. Update KPI Cards & Active Indicator Badge
    updateKPIs(summaryData);
    updateActiveFiltersIndicator(filters);

    // 2. Render 4 Charts with API Data
    if (typeof renderSalesTrend === 'function') renderSalesTrend(monthlyData);
    if (typeof renderRegionChart === 'function') renderRegionChart(regionData);
    if (typeof renderProductChart === 'function') renderProductChart(productData);
    if (typeof renderCustomerChart === 'function') renderCustomerChart(customerData);

  } catch (error) {
    console.error('Error fetching dashboard analytics data:', error);
    showErrorState('Unable to update dashboard data. Please check that the API server is running.');
  }
}

// Event handler for "Apply Filters" button
function handleApplyFilters() {
  const filters = getSelectedFilters();
  loadDashboardData(filters);
}

// Event handler for "Reset Filters" button
function handleResetFilters() {
  const yearSelect = document.getElementById('yearFilter');
  const regionSelect = document.getElementById('regionFilter');
  const categorySelect = document.getElementById('categoryFilter');
  const segmentSelect = document.getElementById('segmentFilter');

  if (yearSelect) yearSelect.value = '';
  if (regionSelect) regionSelect.value = '';
  if (categorySelect) categorySelect.value = '';
  if (segmentSelect) segmentSelect.value = '';

  loadDashboardData(null);
}

// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  loadDashboardData(null);
});
