import React, { useState } from 'react';
import { 
  Download, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  BarChart3, 
  FileText, 
  Globe,
  Settings
} from 'lucide-react';

const ResultsDashboard = ({ report }) => {
  const [activeView, setActiveView] = useState('summary');
  const [selectedUrl, setSelectedUrl] = useState('');
  const [selectedParameter, setSelectedParameter] = useState('');

  if (!report) {
    return (
      <div className="results-dashboard">
        <div className="section-header">
          <h2>ANALYSIS RESULTS DASHBOARD</h2>
        </div>
        <div className="card">
          <div className="card-body text-center">
            <AlertCircle size={48} style={{ margin: '20px 0' }} />
            <h3>NO ANALYSIS DATA AVAILABLE</h3>
            <p>UPLOAD AND ANALYZE A HAR FILE TO VIEW RESULTS</p>
          </div>
        </div>
      </div>
    );
  }

  const handleExportReport = async () => {
    try {
      // This would need the report ID from the backend
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/reports/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(report)
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `harmony_report_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const getFilteredResults = () => {
    let filtered = report.detailed_results;
    
    if (selectedUrl) {
      filtered = filtered.filter(result => 
        result.url.toLowerCase().includes(selectedUrl.toLowerCase())
      );
    }
    
    if (selectedParameter) {
      filtered = filtered.filter(result => 
        result.parameter.toLowerCase().includes(selectedParameter.toLowerCase())
      );
    }
    
    return filtered;
  };

  const getStatusIcon = (result) => {
    return result === 'Pass' ? 
      <CheckCircle size={20} color="green" /> : 
      <XCircle size={20} color="red" />;
  };

  const renderSummary = () => (
    <div className="results-summary">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
        <div className="card">
          <div className="card-header">TOTAL REQUESTS</div>
          <div className="card-body text-center">
            <div style={{ fontSize: '36px', fontWeight: 'bold', margin: '16px 0' }}>
              {report.total_requests}
            </div>
            <Globe size={24} />
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">TOTAL TESTS</div>
          <div className="card-body text-center">
            <div style={{ fontSize: '36px', fontWeight: 'bold', margin: '16px 0' }}>
              {report.total_tests}
            </div>
            <Settings size={24} />
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">PASSED TESTS</div>
          <div className="card-body text-center">
            <div style={{ fontSize: '36px', fontWeight: 'bold', margin: '16px 0', color: 'green' }}>
              {report.passed_tests}
            </div>
            <CheckCircle size={24} color="green" />
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">FAILED TESTS</div>
          <div className="card-body text-center">
            <div style={{ fontSize: '36px', fontWeight: 'bold', margin: '16px 0', color: 'red' }}>
              {report.failed_tests}
            </div>
            <XCircle size={24} color="red" />
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div className="card">
          <div className="card-header">URL FAILURE ANALYSIS</div>
          <div className="card-body">
            {Object.keys(report.url_failures).length === 0 ? (
              <p>NO URL FAILURES DETECTED</p>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>URL</th>
                    <th>FAILURES</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(report.url_failures)
                    .sort(([,a], [,b]) => b - a)
                    .map(([url, count]) => (
                    <tr key={url}>
                      <td style={{ wordBreak: 'break-all' }}>{url}</td>
                      <td><strong>{count}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">PARAMETER FAILURE ANALYSIS</div>
          <div className="card-body">
            {Object.keys(report.dimension_failures).length === 0 ? (
              <p>NO PARAMETER FAILURES DETECTED</p>
            ) : (
              <table className="table">
                <thead>
                  <tr>
                    <th>PARAMETER</th>
                    <th>FAILURES</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(report.dimension_failures)
                    .sort(([,a], [,b]) => b - a)
                    .map(([param, count]) => (
                    <tr key={param}>
                      <td>{param}</td>
                      <td><strong>{count}</strong></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  const renderDetailedResults = () => {
    const filteredResults = getFilteredResults();
    
    return (
      <div className="detailed-results">
        <div className="filters" style={{ marginBottom: '20px', display: 'flex', gap: '16px' }}>
          <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="form-label">FILTER BY URL</label>
            <input
              type="text"
              className="form-input"
              placeholder="Enter URL or domain..."
              value={selectedUrl}
              onChange={(e) => setSelectedUrl(e.target.value)}
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="form-label">FILTER BY PARAMETER</label>
            <input
              type="text"
              className="form-input"
              placeholder="Enter parameter name..."
              value={selectedParameter}
              onChange={(e) => setSelectedParameter(e.target.value)}
            />
          </div>
        </div>
        
        <div className="card">
          <div className="card-header">
            DETAILED TEST RESULTS ({filteredResults.length} OF {report.detailed_results.length})
          </div>
          <div className="card-body">
            <table className="table">
              <thead>
                <tr>
                  <th>STATUS</th>
                  <th>URL</th>
                  <th>PARAMETER</th>
                  <th>TEST CASE</th>
                  <th>DETAILS</th>
                </tr>
              </thead>
              <tbody>
                {filteredResults.map((result, index) => (
                  <tr key={index}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {getStatusIcon(result.result)}
                        <strong>{result.result.toUpperCase()}</strong>
                      </div>
                    </td>
                    <td style={{ wordBreak: 'break-all', maxWidth: '300px' }}>
                      {result.url}
                    </td>
                    <td>{result.parameter}</td>
                    <td>{result.test_case_name}</td>
                    <td>{result.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {filteredResults.length === 0 && (
              <div className="text-center" style={{ padding: '40px' }}>
                <p>NO RESULTS MATCH CURRENT FILTERS</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderRawData = () => (
    <div className="raw-data">
      <div className="card">
        <div className="card-header">
          RAW REQUEST DATA ({report.raw_data.length} REQUESTS)
        </div>
        <div className="card-body">
          <table className="table">
            <thead>
              <tr>
                <th>METHOD</th>
                <th>URL</th>
                <th>STATUS</th>
                <th>PARAMETERS</th>
                <th>PAYLOAD</th>
              </tr>
            </thead>
            <tbody>
              {report.raw_data.map((request, index) => (
                <tr key={index}>
                  <td><strong>{request.method}</strong></td>
                  <td style={{ wordBreak: 'break-all', maxWidth: '300px' }}>
                    {request.url}
                  </td>
                  <td>
                    <span style={{ 
                      color: request.status >= 400 ? 'red' : 
                             request.status >= 300 ? 'orange' : 'green' 
                    }}>
                      {request.status}
                    </span>
                  </td>
                  <td>
                    <details>
                      <summary>{Object.keys(request.parameters).length} PARAMS</summary>
                      <pre style={{ 
                        fontSize: '12px', 
                        margin: '8px 0', 
                        maxHeight: '200px', 
                        overflow: 'auto',
                        background: '#f5f5f5',
                        padding: '8px',
                        border: '1px solid #000'
                      }}>
                        {JSON.stringify(request.parameters, null, 2)}
                      </pre>
                    </details>
                  </td>
                  <td>
                    {request.payload !== 'No payload' ? (
                      <details>
                        <summary>VIEW PAYLOAD</summary>
                        <pre style={{ 
                          fontSize: '12px', 
                          margin: '8px 0', 
                          maxHeight: '200px', 
                          overflow: 'auto',
                          background: '#f5f5f5',
                          padding: '8px',
                          border: '1px solid #000'
                        }}>
                          {request.payload}
                        </pre>
                      </details>
                    ) : (
                      <span>NO PAYLOAD</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  return (
    <div className="results-dashboard">
      <div className="section-header">
        <h2>ANALYSIS RESULTS DASHBOARD</h2>
        <button className="btn btn-primary" onClick={handleExportReport}>
          <Download size={16} />
          EXPORT REPORT
        </button>
      </div>

      <div className="dashboard-nav" style={{ marginBottom: '30px' }}>
        <div className="nav-content">
          {[
            { id: 'summary', label: 'SUMMARY', icon: BarChart3 },
            { id: 'detailed', label: 'DETAILED RESULTS', icon: FileText },
            { id: 'raw', label: 'RAW DATA', icon: Settings }
          ].map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.id}
                className={`nav-tab ${activeView === view.id ? 'active' : ''}`}
                onClick={() => setActiveView(view.id)}
              >
                <Icon size={16} />
                {view.label}
              </button>
            );
          })}
        </div>
      </div>

      {activeView === 'summary' && renderSummary()}
      {activeView === 'detailed' && renderDetailedResults()}
      {activeView === 'raw' && renderRawData()}
    </div>
  );
};

export default ResultsDashboard;