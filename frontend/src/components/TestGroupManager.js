import React, { useState } from 'react';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';
import { BACKEND_URL } from '../config';

const TestGroupManager = ({ testGroups, testCases, onGroupsUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    sequence: [],
    selectedTest: '',
    within_seconds: '',
    on_pass_message: 'Group {name} passed',
    on_fail_message: 'Group {name} failed'
  });
  const [message, setMessage] = useState('');

  const resetForm = () => {
    setFormData({
      name: '',
      sequence: [],
      selectedTest: '',
      within_seconds: '',
      on_pass_message: 'Group {name} passed',
      on_fail_message: 'Group {name} failed'
    });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddTest = () => {
    if (formData.selectedTest) {
      setFormData(prev => ({
        ...prev,
        sequence: [...prev.sequence, prev.selectedTest],
        selectedTest: ''
      }));
    }
  };

  const handleRemoveTest = (index) => {
    setFormData(prev => ({
      ...prev,
      sequence: prev.sequence.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const group = {
        name: formData.name,
        sequence: formData.sequence,
        within_seconds: formData.within_seconds ? parseInt(formData.within_seconds) : null,
        on_pass_message: formData.on_pass_message,
        on_fail_message: formData.on_fail_message
      };
      if (editingGroup) {
        const response = await fetch(`${BACKEND_URL}/api/test-groups/${editingGroup.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ...group, id: editingGroup.id })
        });
        if (response.ok) setMessage('TEST GROUP UPDATED');
      } else {
        const response = await fetch(`${BACKEND_URL}/api/test-groups`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(group)
        });
        if (response.ok) setMessage('TEST GROUP CREATED');
      }
      resetForm();
      setIsEditing(false);
      setEditingGroup(null);
      onGroupsUpdate();
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('ERROR: ' + err.message);
    }
  };

  const handleEdit = (group) => {
    setEditingGroup(group);
    setFormData({
      name: group.name,
      sequence: group.sequence,
      selectedTest: '',
      within_seconds: group.within_seconds || '',
      on_pass_message: group.on_pass_message || 'Group {name} passed',
      on_fail_message: group.on_fail_message || 'Group {name} failed'
    });
    setIsEditing(true);
  };

  const handleDelete = async (groupId) => {
    if (window.confirm('CONFIRM DELETION OF TEST GROUP?')) {
      try {
        const response = await fetch(`${BACKEND_URL}/api/test-groups/${groupId}`, { method: 'DELETE' });
        if (response.ok) {
          setMessage('TEST GROUP DELETED');
          onGroupsUpdate();
          setTimeout(() => setMessage(''), 3000);
        }
      } catch (err) {
        setMessage('ERROR: ' + err.message);
      }
    }
  };

  const handleCancel = () => {
    resetForm();
    setIsEditing(false);
    setEditingGroup(null);
  };

  return (
    <div className="test-group-manager">
      <div className="section-header">
        <h2>TEST GROUP MANAGEMENT</h2>
        {!isEditing && (
          <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
            <Plus size={16} /> NEW TEST GROUP
          </button>
        )}
      </div>
      {message && (
        <div className={`status-message ${message.includes('ERROR') ? 'error' : 'success'}`}>{message}</div>
      )}
      {isEditing && (
        <div className="card">
          <div className="card-header">{editingGroup ? 'EDIT TEST GROUP' : 'CREATE TEST GROUP'}</div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Group Name</label>
                <input type="text" name="name" value={formData.name} onChange={handleInputChange} className="form-input" required />
              </div>
              <div className="form-group">
                <label className="form-label">Add Test to Sequence</label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <select name="selectedTest" value={formData.selectedTest} onChange={handleInputChange} className="form-select" style={{ flex: 1 }}>
                    <option value="">Select test...</option>
                    {testCases.map(tc => (
                      <option key={tc.id} value={tc.name}>{tc.name}</option>
                    ))}
                  </select>
                  <button type="button" className="btn btn-small" onClick={handleAddTest}>ADD</button>
                </div>
                {formData.sequence.length > 0 && (
                  <ul style={{ marginTop: '8px' }}>
                    {formData.sequence.map((t, idx) => (
                      <li key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>{idx + 1}. {t}</span>
                        <button type="button" className="btn btn-small btn-danger" onClick={() => handleRemoveTest(idx)}>REMOVE</button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="form-group">
                <label className="form-label">Pass Message</label>
                <input type="text" name="on_pass_message" value={formData.on_pass_message} onChange={handleInputChange} className="form-input" />
              </div>

              <div className="form-group">
                <label className="form-label">Fail Message</label>
                <input type="text" name="on_fail_message" value={formData.on_fail_message} onChange={handleInputChange} className="form-input" />
              </div>
              <div className="form-group">
                <label className="form-label">Within Seconds (optional)</label>
                <input type="number" name="within_seconds" value={formData.within_seconds} onChange={handleInputChange} className="form-input" />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn btn-primary"><Save size={16} /> {editingGroup ? 'UPDATE' : 'CREATE'}</button>
                <button type="button" className="btn" onClick={handleCancel}><X size={16} /> CANCEL</button>
              </div>
            </form>
          </div>
        </div>
      )}
      <div className="card">
        <div className="card-header">DEFINED TEST GROUPS ({testGroups.length})</div>
        <div className="card-body">
          {testGroups.length === 0 ? (
            <p className="text-center">NO TEST GROUPS DEFINED</p>
          ) : (
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Sequence</th>
                  <th>Within Seconds</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {testGroups.map(group => (
                  <tr key={group.id}>
                    <td>{group.name}</td>
                    <td>{group.sequence.join(' > ')}</td>
                    <td>{group.within_seconds || '-'}</td>
                    <td>
                      <div className="flex gap-2">
                        <button className="btn btn-small" onClick={() => handleEdit(group)}><Edit size={14} /></button>
                        <button className="btn btn-small btn-danger" onClick={() => handleDelete(group.id)}><Trash2 size={14} /></button>
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

export default TestGroupManager;
