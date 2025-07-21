import React, { useState } from 'react';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';
import { BACKEND_URL } from '../config';

const TestCaseManager = ({ testCases, onTestCasesUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editingCase, setEditingCase] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    target_urls: '',
    parameter_name: '',
    condition: 'exists',
    expected_value: '',
    optional: false,
    on_pass_message: 'Parameter {parameter_name} found with value: {value}',
    on_fail_message: 'Parameter {parameter_name} missing or invalid'
  });
  const [message, setMessage] = useState('');

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      target_urls: '',
      parameter_name: '',
      condition: 'exists',
      expected_value: '',
      optional: false,
      on_pass_message: 'Parameter {parameter_name} found with value: {value}',
      on_fail_message: 'Parameter {parameter_name} missing or invalid'
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const testCase = {
        ...formData,
        target_urls: formData.target_urls.split(',').map(url => url.trim()).filter(url => url)
      };
      
      if (editingCase) {
        // Update existing test case
        const response = await fetch(`${BACKEND_URL}/api/test-cases/${editingCase.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...testCase, id: editingCase.id })
        });
        
        if (response.ok) {
          setMessage('TEST CASE UPDATED SUCCESSFULLY');
        }
      } else {
        // Create new test case
        const response = await fetch(`${BACKEND_URL}/api/test-cases`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(testCase)
        });
        
        if (response.ok) {
          setMessage('TEST CASE CREATED SUCCESSFULLY');
        }
      }
      
      resetForm();
      setIsEditing(false);
      setEditingCase(null);
      onTestCasesUpdate();
      
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('ERROR: ' + error.message);
    }
  };

  const handleEdit = (testCase) => {
    setEditingCase(testCase);
    setFormData({
      name: testCase.name,
      description: testCase.description,
      target_urls: testCase.target_urls.join(', '),
      parameter_name: testCase.parameter_name,
      condition: testCase.condition,
      expected_value: testCase.expected_value || '',
      optional: testCase.optional,
      on_pass_message: testCase.on_pass_message,
      on_fail_message: testCase.on_fail_message
    });
    setIsEditing(true);
  };

  const handleDelete = async (testCaseId) => {
    if (window.confirm('CONFIRM DELETION OF TEST CASE?')) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/test-cases/${testCaseId}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          setMessage('TEST CASE DELETED SUCCESSFULLY');
          onTestCasesUpdate();
          setTimeout(() => setMessage(''), 3000);
        }
      } catch (error) {
        setMessage('ERROR: ' + error.message);
      }
    }
  };

  const handleCancel = () => {
    resetForm();
    setIsEditing(false);
    setEditingCase(null);
  };

  return (
    <div className="test-case-manager">
      <div className="section-header">
        <h2>TEST CASE MANAGEMENT SYSTEM</h2>
        {!isEditing && (
          <button 
            className="btn btn-primary"
            onClick={() => setIsEditing(true)}
          >
            <Plus size={16} />
            NEW TEST CASE
          </button>
        )}
      </div>

      {message && (
        <div className={`status-message ${message.includes('ERROR') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {isEditing && (
        <div className="card">
          <div className="card-header">
            {editingCase ? 'EDIT TEST CASE' : 'CREATE NEW TEST CASE'}
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Test Name</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  className="form-textarea"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Target URLs (comma-separated)</label>
                <input
                  type="text"
                  name="target_urls"
                  value={formData.target_urls}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="example.com, api.example.com"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Parameter Name</label>
                <input
                  type="text"
                  name="parameter_name"
                  value={formData.parameter_name}
                  onChange={handleInputChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Condition</label>
                <select
                  name="condition"
                  value={formData.condition}
                  onChange={handleInputChange}
                  className="form-select"
                >
                  <option value="exists">EXISTS</option>
                  <option value="equals">EQUALS</option>
                </select>
              </div>

              {formData.condition === 'equals' && (
                <div className="form-group">
                  <label className="form-label">Expected Value</label>
                  <input
                    type="text"
                    name="expected_value"
                    value={formData.expected_value}
                    onChange={handleInputChange}
                    className="form-input"
                  />
                </div>
              )}

              <div className="form-group">
                <label className="form-label">
                  <input
                    type="checkbox"
                    name="optional"
                    checked={formData.optional}
                    onChange={handleInputChange}
                    style={{ marginRight: '8px' }}
                  />
                  OPTIONAL PARAMETER
                </label>
              </div>

              <div className="form-group">
                <label className="form-label">Success Message</label>
                <input
                  type="text"
                  name="on_pass_message"
                  value={formData.on_pass_message}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Use {value} and {url} placeholders"
                />
              </div>

              <div className="form-group">
                <label className="form-label">Failure Message</label>
                <input
                  type="text"
                  name="on_fail_message"
                  value={formData.on_fail_message}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="Use {url} placeholder"
                />
              </div>

              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary">
                  <Save size={16} />
                  {editingCase ? 'UPDATE' : 'CREATE'}
                </button>
                <button type="button" className="btn" onClick={handleCancel}>
                  <X size={16} />
                  CANCEL
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          ACTIVE TEST CASES ({testCases.length})
        </div>
        <div className="card-body">
          {testCases.length === 0 ? (
            <div className="text-center">
              <p>NO TEST CASES DEFINED</p>
              <p>CREATE YOUR FIRST TEST CASE TO BEGIN QA ANALYSIS</p>
            </div>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Parameter</th>
                  <th>Condition</th>
                  <th>Target URLs</th>
                  <th>Optional</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {testCases.map((testCase) => (
                  <tr key={testCase.id}>
                    <td>
                      <strong>{testCase.name}</strong>
                      <br />
                      <small>{testCase.description}</small>
                    </td>
                    <td>{testCase.parameter_name}</td>
                    <td>
                      {testCase.condition.toUpperCase()}
                      {testCase.expected_value && (
                        <><br /><small>= {testCase.expected_value}</small></>
                      )}
                    </td>
                    <td>
                      {testCase.target_urls.length > 0 
                        ? testCase.target_urls.join(', ')
                        : 'ALL URLS'
                      }
                    </td>
                    <td>{testCase.optional ? 'YES' : 'NO'}</td>
                    <td>
                      <div className="flex gap-2">
                        <button 
                          className="btn btn-small"
                          onClick={() => handleEdit(testCase)}
                        >
                          <Edit size={14} />
                        </button>
                        <button 
                          className="btn btn-small btn-danger"
                          onClick={() => handleDelete(testCase.id)}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default TestCaseManager;