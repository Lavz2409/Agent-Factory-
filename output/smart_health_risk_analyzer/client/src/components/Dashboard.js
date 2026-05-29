javascript
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = () => {
  const [userData, setUserData] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const history = useHistory();

  useEffect(() => {
    // Fetch user data and history
    const fetchUserData = async () => {
      try {
        const response = await axios.get('/api/user/data', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setUserData(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
        history.push('/login');
      }
    };

    fetchUserData();
  }, [history]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/report/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setAnalysisResult(response.data);
      setUploadError('');
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError('Failed to upload file. Please try again.');
    }
  };

  return (
    <div className="dashboard">
      <h1>Smart Health Risk Analyzer Dashboard</h1>
      <div className="upload-section">
        <h2>Upload Medical Report</h2>
        <input type="file" accept=".pdf, .jpg, .jpeg, .png" onChange={handleFileUpload} />
        {uploadError && <p className="error">{uploadError}</p>}
      </div>
      {analysisResult && (
        <div className="analysis-result">
          <h2>Analysis Result</h2>
          <p>Risk Level: {analysisResult.riskLevel}</p>
          <p>Recommendations: {analysisResult.recommendations}</p>
        </div>
      )}
      {userData && (
        <div className="user-history">
          <h2>Your History</h2>
          <ul>
            {userData.history.map((entry, index) => (
              <li key={index}>
                <p>Date: {new Date(entry.date).toLocaleDateString()}</p>
                <p>Risk Level: {entry.riskLevel}</p>
                <p>Recommendations: {entry.recommendations}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Dashboard;