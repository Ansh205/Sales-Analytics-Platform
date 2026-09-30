/**
 * Executive Overview & Page Analytics Controller
 * Sales Analytics Platform (Phase 6.4 & 6.5)
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
    errorMessage.textContent = message || 'Unable to update analytics data. Please check that the API server is running.';
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

// Update KPI card elements with summary API response data
function updateKPIs(data) {
  if (!data) return;

  const kpiSales = document.getElementById('kpi-sales');
  const kpiProfit = document.getElementById('kpi-profit');
  const kpiOrders = document.getElementById('kpi-orders');
  const kpiCustomers = document.getElementById('kpi-customers');
  const kpiMargin = document.getElementById('kpi-margin');
  const kpiReturn = document.getElementById('kpi-return');

  if (kpiSales) kpiSales.textContent = formatCurrency(data.total_sales);
  if (kpiProfit) kpiProfit.textContent = formatCurrency(data.total_profit);
  if (kpiOrders) kpiOrders.textContent = formatNumber(data.total_orders);
  if (kpiCustomers) kpiCustomers.textContent = formatNumber(data.total_customers);
  if (kpiMargin) kpiMargin.textContent = formatPercentage(data.profit_margin);
  if (kpiReturn) kpiReturn.textContent = formatPercentage(data.return_rate);
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

/**
 * 1. EXECUTIVE DASHBOARD PAGE CONTROLLER
 */
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

    updateKPIs(summaryData);
    updateActiveFiltersIndicator(filters);

    if (typeof renderSalesTrend === 'function') renderSalesTrend(monthlyData, 'salesTrendChart');
    if (typeof renderRegionChart === 'function') renderRegionChart(regionData, 'regionChart');
    if (typeof renderProductChart === 'function') renderProductChart(productData, 'productChart');
    if (typeof renderCustomerChart === 'function') renderCustomerChart(customerData, 'customerChart');

  } catch (error) {
    console.error('Error fetching dashboard analytics data:', error);
    showErrorState('Unable to update dashboard data. Please check that the API server is running.');
  }
}

/**
 * 2. PRODUCTS PAGE CONTROLLER
 */
async function loadProductsPage(filters = null) {
  setLoadingState();
  const queryString = buildQueryString(filters);

  const summaryUrl = `/api/summary${queryString}`;
  const productUrl = `/api/products/top${queryString ? queryString + '&limit=10' : '?limit=10'}`;

  try {
    const [summaryData, productData] = await Promise.all([
      fetchEndpoint(summaryUrl),
      fetchEndpoint(productUrl)
    ]);

    updateKPIs(summaryData);
    updateActiveFiltersIndicator(filters);

    if (typeof renderProductChart === 'function') {
      renderProductChart(productData, 'productPageChart');
    }

    populateProductTable(productData);

  } catch (error) {
    console.error('Error loading products page analytics:', error);
    showErrorState('Unable to load product analytics. Please check that the API server is running.');
  }
}

function populateProductTable(products) {
  const tbody = document.getElementById('productTableBody');
  if (!tbody) return;

  if (!products || !Array.isArray(products) || products.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">No products available for the selected filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = products.map((item, index) => {
    const profitClass = Number(item.profit) >= 0 ? 'positive-profit' : 'negative-profit';
    return `
      <tr>
        <td><span class="rank-badge">${index + 1}</span></td>
        <td style="font-weight: 500;">${item.product_name || 'Unknown Product'}</td>
        <td><span class="badge-category">${item.category || 'N/A'}</span></td>
        <td><span class="badge-segment">${item.sub_category || 'N/A'}</span></td>
        <td class="text-right" style="font-weight: 600;">${formatCurrency(item.sales)}</td>
        <td class="text-right ${profitClass}">${formatCurrency(item.profit)}</td>
      </tr>`;
  }).join('');
}

/**
 * 3. CUSTOMERS PAGE CONTROLLER
 */
async function loadCustomersPage(filters = null) {
  setLoadingState();
  const queryString = buildQueryString(filters);

  const summaryUrl = `/api/summary${queryString}`;
  const customerUrl = `/api/customers/top${queryString ? queryString + '&limit=10' : '?limit=10'}`;

  try {
    const [summaryData, customerData] = await Promise.all([
      fetchEndpoint(summaryUrl),
      fetchEndpoint(customerUrl)
    ]);

    updateKPIs(summaryData);
    updateActiveFiltersIndicator(filters);

    if (typeof renderCustomerChart === 'function') {
      renderCustomerChart(customerData, 'customerPageChart');
    }

    populateCustomerTable(customerData);

  } catch (error) {
    console.error('Error loading customers page analytics:', error);
    showErrorState('Unable to load customer analytics. Please check that the API server is running.');
  }
}

function populateCustomerTable(customers) {
  const tbody = document.getElementById('customerTableBody');
  if (!tbody) return;

  if (!customers || !Array.isArray(customers) || customers.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No customers available for the selected filters.</td></tr>`;
    return;
  }

  tbody.innerHTML = customers.map((item, index) => {
    const profitClass = Number(item.profit) >= 0 ? 'positive-profit' : 'negative-profit';
    return `
      <tr>
        <td><span class="rank-badge">${index + 1}</span></td>
        <td style="font-weight: 500;">${item.customer_name || 'Unknown Customer'}</td>
        <td><span class="badge-segment">${item.segment || 'N/A'}</span></td>
        <td class="text-right" style="font-weight: 600;">${formatCurrency(item.sales)}</td>
        <td class="text-right ${profitClass}">${formatCurrency(item.profit)}</td>
      </tr>`;
  }).join('');
}

/**
 * 4. REGIONS PAGE CONTROLLER
 */
async function loadRegionsPage(filters = null) {
  setLoadingState();
  const queryString = buildQueryString(filters);

  const summaryUrl = `/api/summary${queryString}`;
  const regionUrl = `/api/sales/region${queryString}`;

  try {
    const [summaryData, regionData] = await Promise.all([
      fetchEndpoint(summaryUrl),
      fetchEndpoint(regionUrl)
    ]);

    updateKPIs(summaryData);
    updateActiveFiltersIndicator(filters);

    if (typeof renderRegionChart === 'function') {
      renderRegionChart(regionData, 'regionPageChart');
    }

    populateRegionTable(regionData);

  } catch (error) {
    console.error('Error loading regional page analytics:', error);
    showErrorState('Unable to load regional analytics. Please check that the API server is running.');
  }
}

function populateRegionTable(regions) {
  const tbody = document.getElementById('regionTableBody');
  if (!tbody) return;

  if (!regions || !Array.isArray(regions) || regions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No regional data available for the selected filters.</td></tr>`;
    return;
  }

  // Sort descending by sales for display table
  const sortedRegions = [...regions].sort((a, b) => Number(b.sales) - Number(a.sales));

  tbody.innerHTML = sortedRegions.map((item, index) => {
    const profitClass = Number(item.profit) >= 0 ? 'positive-profit' : 'negative-profit';
    return `
      <tr>
        <td><span class="rank-badge">${index + 1}</span></td>
        <td style="font-weight: 600;">${item.region || 'Unknown Region'} Region</td>
        <td class="text-right" style="font-weight: 600;">${formatCurrency(item.sales)}</td>
        <td class="text-right ${profitClass}">${formatCurrency(item.profit)}</td>
        <td class="text-right" style="font-weight: 500;">${formatNumber(item.orders)}</td>
      </tr>`;
  }).join('');
}

// Universal event handler for "Apply Filters" button across all pages
function handleApplyFilters() {
  const filters = getSelectedFilters();
  dispatchPageLoader(filters);
}

// Universal event handler for "Reset Filters" button across all pages
function handleResetFilters() {
  const yearSelect = document.getElementById('yearFilter');
  const regionSelect = document.getElementById('regionFilter');
  const categorySelect = document.getElementById('categoryFilter');
  const segmentSelect = document.getElementById('segmentFilter');

  if (yearSelect) yearSelect.value = '';
  if (regionSelect) regionSelect.value = '';
  if (categorySelect) categorySelect.value = '';
  if (segmentSelect) segmentSelect.value = '';

  dispatchPageLoader(null);
}

// Router dispatcher to invoke page loader based on active element containers
function dispatchPageLoader(filters = null) {
  if (document.getElementById('salesTrendChart')) {
    loadDashboardData(filters);
  } else if (document.getElementById('productPageChart')) {
    loadProductsPage(filters);
  } else if (document.getElementById('customerPageChart')) {
    loadCustomersPage(filters);
  } else if (document.getElementById('regionPageChart')) {
    loadRegionsPage(filters);
  }
}

// Initialize active page on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  dispatchPageLoader(null);
});
