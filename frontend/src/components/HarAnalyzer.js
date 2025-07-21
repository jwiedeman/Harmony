import React, { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Play, CheckCircle, XCircle, Folder, Clock } from 'lucide-react';
import { BACKEND_URL } from '../config';

const HarAnalyzer = ({ onAnalysisComplete }) => {
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [message, setMessage] = useState('');
  const [availableHarFiles, setAvailableHarFiles] = useState([]);
  const [selectedHarFile, setSelectedHarFile] = useState(null);
  const fileInputRef = useRef(null);

  // Fetch available HAR files on component mount
  useEffect(() => {
    fetchAvailableHarFiles();
  }, []);

  const fetchAvailableHarFiles = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/har-files`);
      const data = await response.json();
      setAvailableHarFiles(data.har_files || []);
    } catch (error) {
      console.error('Error fetching available HAR files:', error);
    }
  };

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.name.endsWith('.har')) {
      setFile(selectedFile);
      setSelectedHarFile(null); // Clear selected existing file
      setMessage('');
    } else {
      setMessage('ERROR: Please select a valid HAR file');
      setFile(null);
    }
  };

  const handleExistingFileSelect = (harFile) => {
    setSelectedHarFile(harFile);
    setFile(null); // Clear uploaded file
    setMessage('');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    handleFileSelect(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files[0];
    handleFileSelect(selectedFile);
  };

  const handleAnalyze = async () => {
    if (!file && !selectedHarFile) {
      setMessage('ERROR: Please select a HAR file first');
      return;
    }

    setIsAnalyzing(true);
    setMessage('ANALYZING HAR FILE...');

    try {
      let response;
      
      if (selectedHarFile) {
        // Analyze existing HAR file
        response = await fetch(`${BACKEND_URL}/api/analyze-har-file/${selectedHarFile.filename}`, {
          method: 'POST',
        });
      } else {
        // Analyze uploaded HAR file
        const formData = new FormData();
        formData.append('file', file);

        response = await fetch(`${BACKEND_URL}/api/analyze-har`, {
          method: 'POST',
          body: formData,
        });
      }

      const data = await response.json();

      if (response.ok) {
        setMessage('ANALYSIS COMPLETED SUCCESSFULLY');
        onAnalysisComplete(data.report);
        setTimeout(() => setMessage(''), 2000);
      } else {
        setMessage('ERROR: ' + (data.detail || 'Analysis failed'));
      }
    } catch (error) {
      setMessage('ERROR: ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimestamp = (timestamp) => {
    return new Date(parseFloat(timestamp) * 1000).toLocaleString();
  };

  return (
    <div className="har-analyzer">
      <div className="section-header">
        <h2>HAR FILE ANALYSIS SYSTEM</h2>
      </div>

      {message && (
        <div className={`status-message ${message.includes('ERROR') ? 'error' : 
                         message.includes('ANALYZING') ? 'info' : 'success'}`}>
          {message}
        </div>
      )}

      {/* Available HAR Files Section */}
      {availableHarFiles.length > 0 && (
        <div className="card">
          <div className="card-header">
            AVAILABLE HAR FILES ({availableHarFiles.length})
          </div>
          <div className="card-body">
            <div className="har-files-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              {availableHarFiles.map((harFile, index) => (
                <div
                  key={index}
                  className={`har-file-card ${selectedHarFile?.filename === harFile.filename ? 'selected' : ''}`}
                  style={{
                    border: '2px solid #000000',
                    padding: '16px',
                    backgroundColor: selectedHarFile?.filename === harFile.filename ? '#f0f0f0' : '#ffffff',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onClick={() => handleExistingFileSelect(harFile)}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <FileText size={20} />
                    <strong>{harFile.filename}</strong>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                      <Folder size={14} />
                      SIZE: {formatFileSize(harFile.size)}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Clock size={14} />
                      MODIFIED: {formatTimestamp(harFile.modified)}
                    </div>
                  </div>
                  {selectedHarFile?.filename === harFile.filename && (
                    <div style={{ marginTop: '8px', color: '#000000', fontWeight: 'bold', fontSize: '12px' }}>
                      ✓ SELECTED FOR ANALYSIS
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {selectedHarFile && (
              <div className="selected-file-info" style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '16px', 
                border: '1px solid #000000',
                marginBottom: '16px'
              }}>
                <h4>SELECTED FILE: {selectedHarFile.filename}</h4>
                <p>Path: {selectedHarFile.path}</p>
                <p>Size: {formatFileSize(selectedHarFile.size)}</p>
                <p>Modified: {formatTimestamp(selectedHarFile.modified)}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upload Section */}
      <div className="card">
        <div className="card-header">
          FILE UPLOAD INTERFACE
        </div>
        <div className="card-body">
          <div
            className={`upload-area ${dragOver ? 'drag-over' : ''} ${isAnalyzing ? 'uploading' : ''}`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".har"
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />
            
            <div className="upload-content">
              <Upload size={48} style={{ marginBottom: '16px' }} />
              <h3>DROP HAR FILE HERE OR CLICK TO SELECT</h3>
              <p>SUPPORTED FORMAT: .HAR (HTTP ARCHIVE)</p>
              <p style={{ fontSize: '12px', marginTop: '8px' }}>
                OR SELECT FROM AVAILABLE FILES ABOVE
              </p>
              {file && (
                <div className="file-info" style={{ marginTop: '20px' }}>
                  <div className="flex items-center" style={{ justifyContent: 'center', gap: '8px' }}>
                    <FileText size={20} />
                    <strong>{file.name}</strong>
                  </div>
                  <p>SIZE: {formatFileSize(file.size)}</p>
                  <p>LAST MODIFIED: {new Date(file.lastModified).toLocaleString()}</p>
                </div>
              )}
            </div>
          </div>

          {(file || selectedHarFile) && (
            <div className="mt-2">
              <button
                className="btn btn-primary"
                onClick={handleAnalyze}
                disabled={isAnalyzing}
                style={{ width: '100%' }}
              >
                {isAnalyzing ? (
                  <>ANALYZING...</>
                ) : (
                  <>
                    <Play size={16} />
                    START ANALYSIS
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          ANALYSIS INFORMATION
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            <div>
              <h4>WHAT IS HAR FILE ANALYSIS?</h4>
              <ul style={{ listStyle: 'none', padding: 0, marginTop: '12px' }}>
                <li>• EXAMINES HTTP NETWORK TRAFFIC</li>
                <li>• VALIDATES API PARAMETERS</li>
                <li>• IDENTIFIES MISSING OR INCORRECT DATA</li>
                <li>• GENERATES COMPREHENSIVE QA REPORTS</li>
              </ul>
            </div>
            
            <div>
              <h4>ANALYSIS PROCESS</h4>
              <ul style={{ listStyle: 'none', padding: 0, marginTop: '12px' }}>
                <li>• PARSE HAR FILE ENTRIES</li>
                <li>• APPLY DEFINED TEST CASES</li>
                <li>• EVALUATE PARAMETER CONDITIONS</li>
                <li>• COMPILE FAILURE REPORTS</li>
              </ul>
            </div>
            
            <div>
              <h4>REQUIREMENTS</h4>
              <ul style={{ listStyle: 'none', padding: 0, marginTop: '12px' }}>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {(file || selectedHarFile) ? <CheckCircle size={16} color="green" /> : <XCircle size={16} />}
                  VALID HAR FILE SELECTED
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={16} color="green" />
                  TEST CASES CONFIGURED
                </li>
                <li style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <CheckCircle size={16} color="green" />
                  SYSTEM OPERATIONAL
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          HOW TO OBTAIN HAR FILES
        </div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
            <div>
              <h4>CHROME BROWSER</h4>
              <ol style={{ paddingLeft: '20px', marginTop: '8px' }}>
                <li>OPEN DEVELOPER TOOLS (F12)</li>
                <li>GO TO NETWORK TAB</li>
                <li>PERFORM ACTIONS ON WEBSITE</li>
                <li>RIGHT-CLICK → SAVE ALL AS HAR</li>
              </ol>
            </div>
            
            <div>
              <h4>FIREFOX BROWSER</h4>
              <ol style={{ paddingLeft: '20px', marginTop: '8px' }}>
                <li>OPEN DEVELOPER TOOLS (F12)</li>
                <li>GO TO NETWORK TAB</li>
                <li>PERFORM ACTIONS ON WEBSITE</li>
                <li>CLICK GEAR ICON → SAVE ALL AS HAR</li>
              </ol>
            </div>
            
            <div>
              <h4>SAFARI BROWSER</h4>
              <ol style={{ paddingLeft: '20px', marginTop: '8px' }}>
                <li>ENABLE DEVELOP MENU</li>
                <li>OPEN WEB INSPECTOR</li>
                <li>GO TO NETWORK TAB</li>
                <li>EXPORT AS HAR FILE</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HarAnalyzer;