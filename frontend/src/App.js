import React, { useState, useEffect } from 'react';
import './App.css';
import TestCaseManager from './components/TestCaseManager';
import TestGroupManager from './components/TestGroupManager';
import HarAnalyzer from './components/HarAnalyzer';
import ResultsDashboard from './components/ResultsDashboard';
import { FileText, Upload, BarChart3, Settings, Layers } from 'lucide-react';
import { BACKEND_URL } from './config';
import { Feature16 } from './components/Feature16';

const App = () => {
  const [activeTab, setActiveTab] = useState('test-cases');
  const [testCases, setTestCases] = useState([]);
  const [testGroups, setTestGroups] = useState([]);
  const [analysisReport, setAnalysisReport] = useState(null);

  const tabs = [
    { id: 'test-cases', label: 'TEST CASES', icon: Settings },
    { id: 'test-groups', label: 'TEST GROUPS', icon: Layers },
    { id: 'analyzer', label: 'HAR ANALYZER', icon: Upload },
    { id: 'results', label: 'RESULTS', icon: BarChart3 }
  ];

  // Fetch test cases and groups on load
  useEffect(() => {
    fetchTestCases();
    fetchTestGroups();
  }, []);

  const fetchTestCases = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/test-cases`);
      const data = await response.json();
      setTestCases(data.test_cases || []);
    } catch (error) {
      console.error('Error fetching test cases:', error);
    }
  };

  const fetchTestGroups = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/test-groups`);
      const data = await response.json();
      setTestGroups(data.test_groups || []);
    } catch (error) {
      console.error('Error fetching test groups:', error);
    }
  };

  const handleAnalysisComplete = (report) => {
    setAnalysisReport(report);
    setActiveTab('results');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'test-cases':
        return <TestCaseManager testCases={testCases} onTestCasesUpdate={fetchTestCases} />;
      case 'test-groups':
        return <TestGroupManager testGroups={testGroups} testCases={testCases} onGroupsUpdate={fetchTestGroups} />;
      case 'analyzer':
        return <HarAnalyzer onAnalysisComplete={handleAnalysisComplete} />;
      case 'results':
        return <ResultsDashboard report={analysisReport} />;
      default:
        return <TestCaseManager testCases={testCases} onTestCasesUpdate={fetchTestCases} />;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <FileText size={32} />
            <h1>HARMONY QA SYSTEM</h1>
          </div>
          <div className="status-section">
            <div className="status-indicator">
              <div className="status-dot active"></div>
              <span>SYSTEM OPERATIONAL</span>
            </div>
          </div>
        </div>
      </header>

      <nav className="app-nav">
        <div className="nav-content">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <Icon size={20} />
                {tab.label}
              </button>
            );
          })}
        </div>
      </nav>

      <main className="app-main">
        <Feature16 />
        <div className="main-content">
          {renderContent()}
        </div>
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <span>HARMONY QA v1.0 | HTTP ARCHIVE ANALYSIS SYSTEM</span>
          <span>{new Date().toISOString().split('T')[0]} {new Date().toTimeString().split(' ')[0]}</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
