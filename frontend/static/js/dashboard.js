const API_BASE_URL = window.location.origin;

// Utility Functions
const showLoading = (elementId) => {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="loading">
                <div class="loading-spinner"></div>
                <p>Loading data...</p>
            </div>
        `;
    }
};

const showError = (elementId, message) => {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="error-message">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
};

const showSuccess = (elementId, message) => {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="success-message">
                <strong>Success:</strong> ${message}
            </div>
        `;
    }
};

// API Functions
const apiCall = async (endpoint, method = 'GET', body = null) => {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
};

const loadDatasets = async () => {
    const button = document.getElementById('loadDatasetsBtn');
    if (button) button.disabled = true;
    
    showLoading('datasetsStatus');
    
    try {
        const result = await apiCall('/api/datasets/load', 'POST');
        
        if (result.status === 'success') {
            displayDatasetStats(result.datasets);
            showSuccess('datasetsStatus', 'Datasets loaded successfully');
        }
    } catch (error) {
        showError('datasetsStatus', error.message);
    } finally {
        if (button) button.disabled = false;
    }
};

const trainModels = async () => {
    const button = document.getElementById('trainModelsBtn');
    if (button) button.disabled = true;
    
    showLoading('trainingStatus');
    
    try {
        const result = await apiCall('/api/models/train', 'POST');
        
        if (result.status === 'success') {
            showSuccess('trainingStatus', 'Models trained successfully');
            await loadAllVisualizations();
        }
    } catch (error) {
        showError('trainingStatus', error.message);
    } finally {
        if (button) button.disabled = false;
    }
};

const displayDatasetStats = (datasets) => {
    const container = document.getElementById('datasetsStatus');
    if (!container) return;
    
    let html = '<div class="stats-grid">';
    
    for (const [name, stats] of Object.entries(datasets)) {
        html += `
            <div class="stat-card">
                <h4>${name.toUpperCase()}</h4>
                <div class="value">${stats.processed_records.toLocaleString()}</div>
                <div class="label">Processed Records</div>
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
};

// Visualization Functions
const createFairnessComparisonChart = async () => {
    showLoading('fairnessComparisonChart');
    
    try {
        const result = await apiCall('/api/visualizations/fairness-comparison');
        
        if (result.status === 'success' && result.data.length > 0) {
            const data = result.data;
            
            const traces = [];
            const datasets = [...new Set(data.map(d => d.dataset))];
            
            datasets.forEach(dataset => {
                const datasetData = data.filter(d => d.dataset === dataset);
                
                traces.push({
                    x: datasetData.map(d => d.model),
                    y: datasetData.map(d => d.demographic_parity_diff),
                    name: dataset,
                    type: 'bar'
                });
            });
            
            const layout = {
                title: 'Demographic Parity Difference by Model',
                xaxis: { title: 'Model' },
                yaxis: { title: 'Demographic Parity Difference' },
                barmode: 'group',
                height: 400
            };
            
            Plotly.newPlot('fairnessComparisonChart', traces, layout);
        }
    } catch (error) {
        showError('fairnessComparisonChart', error.message);
    }
};

const createPerformanceMetricsChart = async () => {
    showLoading('performanceMetricsChart');
    
    try {
        const result = await apiCall('/api/visualizations/performance-metrics');
        
        if (result.status === 'success' && result.data.length > 0) {
            const data = result.data;
            
            const traces = [];
            const datasets = [...new Set(data.map(d => d.dataset))];
            
            datasets.forEach(dataset => {
                const datasetData = data.filter(d => d.dataset === dataset);
                
                traces.push({
                    x: datasetData.map(d => d.model),
                    y: datasetData.map(d => d.accuracy),
                    name: dataset,
                    type: 'bar'
                });
            });
            
            const layout = {
                title: 'Model Accuracy Comparison',
                xaxis: { title: 'Model' },
                yaxis: { title: 'Accuracy', range: [0, 1] },
                barmode: 'group',
                height: 400
            };
            
            Plotly.newPlot('performanceMetricsChart', traces, layout);
        }
    } catch (error) {
        showError('performanceMetricsChart', error.message);
    }
};

const createBiasDeltaChart = async () => {
    showLoading('biasDeltaChart');
    
    try {
        const result = await apiCall('/api/visualizations/bias-delta');
        
        if (result.status === 'success' && result.data.length > 0) {
            const data = result.data;
            
            const trace = {
                x: data.map(d => d.dataset),
                y: data.map(d => d.mean_bias_delta),
                type: 'bar',
                marker: {
                    color: data.map(d => d.mean_bias_delta),
                    colorscale: 'RdYlGn',
                    reversescale: true
                }
            };
            
            const layout = {
                title: 'Bias Delta Score by Dataset',
                xaxis: { title: 'Dataset' },
                yaxis: { title: 'Mean Bias Delta Score' },
                height: 400
            };
            
            Plotly.newPlot('biasDeltaChart', [trace], layout);
        }
    } catch (error) {
        showError('biasDeltaChart', error.message);
    }
};

const createStabilityIndexChart = async () => {
    showLoading('stabilityIndexChart');
    
    try {
        const result = await apiCall('/api/visualizations/stability-index');
        
        if (result.status === 'success' && result.data.length > 0) {
            const data = result.data;
            
            const trace = {
                x: data.map(d => d.dataset),
                y: data.map(d => d.fairness_stability_index),
                type: 'bar',
                marker: {
                    color: data.map(d => d.fairness_stability_index),
                    colorscale: 'RdYlGn'
                }
            };
            
            const layout = {
                title: 'Fairness Stability Index by Dataset',
                xaxis: { title: 'Dataset' },
                yaxis: { title: 'Fairness Stability Index', range: [0, 1] },
                height: 400
            };
            
            Plotly.newPlot('stabilityIndexChart', [trace], layout);
        }
    } catch (error) {
        showError('stabilityIndexChart', error.message);
    }
};

const createTradeoffChart = async () => {
    showLoading('tradeoffChart');
    
    try {
        const perfResult = await apiCall('/api/visualizations/performance-metrics');
        const fairnessResult = await apiCall('/api/visualizations/fairness-comparison');
        
        if (perfResult.status === 'success' && fairnessResult.status === 'success') {
            const perfData = perfResult.data;
            const fairnessData = fairnessResult.data;
            
            const combinedData = perfData.map(p => {
                const f = fairnessData.find(fd => 
                    fd.dataset === p.dataset && fd.model === p.model
                );
                return {
                    ...p,
                    bias_score: f ? Math.abs(f.demographic_parity_diff) : 0
                };
            });
            
            const datasets = [...new Set(combinedData.map(d => d.dataset))];
            const traces = [];
            
            datasets.forEach(dataset => {
                const datasetData = combinedData.filter(d => d.dataset === dataset);
                
                traces.push({
                    x: datasetData.map(d => d.bias_score),
                    y: datasetData.map(d => d.accuracy),
                    mode: 'markers+text',
                    name: dataset,
                    text: datasetData.map(d => d.model),
                    textposition: 'top center',
                    marker: { size: 12 }
                });
            });
            
            const layout = {
                title: 'Performance vs Fairness Trade-off',
                xaxis: { title: 'Bias Score (lower is better)' },
                yaxis: { title: 'Accuracy', range: [0.5, 1] },
                height: 500
            };
            
            Plotly.newPlot('tradeoffChart', traces, layout);
        }
    } catch (error) {
        showError('tradeoffChart', error.message);
    }
};

const loadGovernanceData = async () => {
    showLoading('governanceData');
    
    try {
        const registryResult = await apiCall('/api/governance/registry');
        const complianceResult = await apiCall('/api/governance/compliance');
        const auditResult = await apiCall('/api/governance/audit-log');
        
        if (registryResult.status === 'success') {
            displayGovernanceStats(
                registryResult.registry,
                complianceResult.compliance_report,
                auditResult.audit_log
            );
        }
    } catch (error) {
        showError('governanceData', error.message);
    }
};

const displayGovernanceStats = (registry, compliance, auditLog) => {
    const container = document.getElementById('governanceData');
    if (!container) return;
    
    const totalModels = Object.keys(registry).length;
    const compliantModels = compliance.compliant_models;
    const complianceRate = (compliance.compliance_rate * 100).toFixed(1);
    
    let html = `
        <div class="stats-grid">
            <div class="stat-card">
                <h4>Total Models</h4>
                <div class="value">${totalModels}</div>
                <div class="label">Registered</div>
            </div>
            <div class="stat-card success">
                <h4>Compliant Models</h4>
                <div class="value">${compliantModels}</div>
                <div class="label">Meeting Standards</div>
            </div>
            <div class="stat-card ${complianceRate >= 80 ? 'success' : 'warning'}">
                <h4>Compliance Rate</h4>
                <div class="value">${complianceRate}%</div>
                <div class="label">Overall</div>
            </div>
            <div class="stat-card">
                <h4>Audit Entries</h4>
                <div class="value">${auditLog.length}</div>
                <div class="label">Total Logs</div>
            </div>
        </div>
        
        <div class="table-container">
            <h3>Model Registry</h3>
            <table>
                <thead>
                    <tr>
                        <th>Version ID</th>
                        <th>Model</th>
                        <th>Dataset</th>
                        <th>Accuracy</th>
                        <th>Compliance</th>
                        <th>Registered</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const [versionId, model] of Object.entries(registry)) {
        const isCompliant = model.compliance_status.compliant;
        const badgeClass = isCompliant ? 'badge-success' : 'badge-danger';
        const badgeText = isCompliant ? 'Compliant' : 'Non-Compliant';
        
        html += `
            <tr>
                <td>${versionId}</td>
                <td>${model.model_name}</td>
                <td>${model.dataset}</td>
                <td>${(model.performance_metrics.accuracy * 100).toFixed(1)}%</td>
                <td><span class="badge ${badgeClass}">${badgeText}</span></td>
                <td>${new Date(model.registration_timestamp).toLocaleString()}</td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
};

const loadAlerts = async () => {
    showLoading('alertsList');
    
    try {
        const result = await apiCall('/api/alerts');
        
        if (result.status === 'success') {
            displayAlerts(result.alerts);
        }
    } catch (error) {
        showError('alertsList', error.message);
    }
};

const displayAlerts = (alerts) => {
    const container = document.getElementById('alertsList');
    if (!container) return;
    
    if (alerts.length === 0) {
        container.innerHTML = '<div class="info-message">No alerts generated. All models within fairness thresholds.</div>';
        return;
    }
    
    let html = '';
    
    alerts.forEach(alert => {
        const severityClass = alert.severity.toLowerCase();
        
        html += `
            <div class="alert-item ${severityClass}">
                <div class="alert-header">
                    <div class="alert-title">${alert.alert_type}</div>
                    <span class="badge badge-${severityClass === 'critical' ? 'danger' : severityClass === 'high' ? 'warning' : 'info'}">${alert.severity}</span>
                </div>
                <div class="alert-body">${alert.message}</div>
                <div class="alert-metrics">
                    <div class="alert-metric">
                        <div class="alert-metric-label">Model</div>
                        <div class="alert-metric-value">${alert.model}</div>
                    </div>
                    <div class="alert-metric">
                        <div class="alert-metric-label">Dataset</div>
                        <div class="alert-metric-value">${alert.dataset}</div>
                    </div>
                    <div class="alert-metric">
                        <div class="alert-metric-label">Metric Value</div>
                        <div class="alert-metric-value">${alert.metric_value.toFixed(4)}</div>
                    </div>
                    <div class="alert-metric">
                        <div class="alert-metric-label">Threshold</div>
                        <div class="alert-metric-value">${alert.threshold}</div>
                    </div>
                    <div class="alert-metric">
                        <div class="alert-metric-label">Time</div>
                        <div class="alert-metric-value">${new Date(alert.timestamp).toLocaleTimeString()}</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
};

const loadSalesforceRegistry = async () => {
    showLoading('salesforceRegistry');
    
    try {
        const result = await apiCall('/api/salesforce/registry');
        
        if (result.status === 'success') {
            displaySalesforceRegistry(result.salesforce_registry);
        }
    } catch (error) {
        showError('salesforceRegistry', error.message);
    }
};

const displaySalesforceRegistry = (registry) => {
    const container = document.getElementById('salesforceRegistry');
    if (!container) return;
    
    let html = `
        <div class="table-container">
            <h3>Salesforce AI Model Registry</h3>
            <table>
                <thead>
                    <tr>
                        <th>SF Model ID</th>
                        <th>Model Name</th>
                        <th>Dataset</th>
                        <th>Compliance Score</th>
                        <th>Deployment Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    registry.forEach(model => {
        const score = model.compliance_status.compliance_score;
        const scoreClass = score >= 75 ? 'success' : score >= 50 ? 'warning' : 'danger';
        const canDeploy = model.compliance_status.compliant && model.deployment_status !== 'DEPLOYED';
        
        html += `
            <tr>
                <td>${model.salesforce_model_id}</td>
                <td>${model.model_name}</td>
                <td>${model.dataset}</td>
                <td><span class="badge badge-${scoreClass}">${score}/100</span></td>
                <td><span class="badge badge-info">${model.deployment_status}</span></td>
                <td>
                    <button class="btn-primary" 
                            onclick="deployModel('${model.salesforce_model_id}')"
                            ${!canDeploy ? 'disabled' : ''}>
                        Deploy
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
};

const deployModel = async (modelId) => {
    try {
        const result = await apiCall(`/api/salesforce/deploy/${modelId}`, 'POST');
        
        if (result.status === 'success') {
            alert('Model deployed successfully!');
            await loadSalesforceRegistry();
        }
    } catch (error) {
        alert(`Deployment failed: ${error.message}`);
    }
};

const loadAllVisualizations = async () => {
    if (document.getElementById('fairnessComparisonChart')) {
        await createFairnessComparisonChart();
    }
    if (document.getElementById('performanceMetricsChart')) {
        await createPerformanceMetricsChart();
    }
    if (document.getElementById('biasDeltaChart')) {
        await createBiasDeltaChart();
    }
    if (document.getElementById('stabilityIndexChart')) {
        await createStabilityIndexChart();
    }
    if (document.getElementById('tradeoffChart')) {
        await createTradeoffChart();
    }
    if (document.getElementById('governanceData')) {
        await loadGovernanceData();
    }
    if (document.getElementById('alertsList')) {
        await loadAlerts();
    }
    if (document.getElementById('salesforceRegistry')) {
        await loadSalesforceRegistry();
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Set active navigation
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Load initial data
    loadAllVisualizations();
});