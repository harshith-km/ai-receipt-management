import React, { useState } from 'react';
import axios from 'axios';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Pie, Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError('Please select a valid image file (JPG, PNG, etc.)');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const uploadReceipt = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError(null);
    setResults(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResults(response.data);
      } else {
        setError(response.data.error || 'Failed to process receipt');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload and process receipt');
    } finally {
      setIsUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setResults(null);
    setError(null);
    setIsUploading(false);
  };

  const getCategoryClass = (category) => {
    return `category-${category.toLowerCase()}`;
  };

  const prepareChartData = () => {
    if (!results || !results.ai_analysis) return null;

    // Extract items from AI analysis
    const items = results.ai_analysis.items || [];
    const categoryTotals = {};
    
    items.forEach(item => {
      const category = item.category || 'Other';
      categoryTotals[category] = (categoryTotals[category] || 0) + item.amount;
    });

    const categories = Object.keys(categoryTotals);
    const amounts = Object.values(categoryTotals);

    const colors = [
      '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
      '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
    ];

    return {
      labels: categories,
      datasets: [
        {
          data: amounts,
          backgroundColor: colors.slice(0, categories.length),
          borderColor: colors.slice(0, categories.length),
          borderWidth: 2,
        },
      ],
    };
  };

  const chartData = prepareChartData();

  return (
    <div className="container">
      <div className="header">
        <h1>🧾 Smart Expense Tracker</h1>
        <p>Upload your receipt and let AI categorize your expenses automatically</p>
      </div>

      <div className="card">
        <div
          className={`upload-area ${dragActive ? 'dragover' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById('file-input').click()}
        >
          <div className="upload-icon">📄</div>
          <div className="upload-text">
            {file ? `Selected: ${file.name}` : 'Click to upload or drag & drop your receipt'}
          </div>
          <div className="upload-subtext">
            Supports JPG, PNG, and other image formats
          </div>
          <input
            id="file-input"
            type="file"
            className="file-input"
            accept="image/*"
            onChange={handleFileInput}
          />
        </div>

        {error && <div className="error">{error}</div>}

        <div style={{ textAlign: 'center', marginTop: '20px' }}>
          <button
            className="btn"
            onClick={uploadReceipt}
            disabled={!file || isUploading}
          >
            {isUploading ? (
              <div className="loading">
                <div className="spinner"></div>
                Processing...
              </div>
            ) : (
              'Process Receipt'
            )}
          </button>
          
          {results && (
            <button className="btn btn-secondary" onClick={resetForm}>
              Upload Another Receipt
            </button>
          )}
        </div>
      </div>

      {results && (
        <div className="results-section">
          <div className="card">
            <h2 className="section-title">📊 Expense Summary</h2>
            
            <div className="summary-cards">
              <div className="summary-card">
                <h3>Total Amount</h3>
                <div className="amount">₹{results.ai_analysis?.total_amount?.toFixed(2) || '0.00'}</div>
              </div>
              <div className="summary-card">
                <h3>Items Found</h3>
                <div className="amount">{results.ai_analysis?.items?.length || 0}</div>
              </div>
              <div className="summary-card">
                <h3>Categories</h3>
                <div className="amount">{results.ai_analysis?.items ? 
                  new Set(results.ai_analysis.items.map(item => item.category)).size : 0}</div>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="section-title">📋 Expense Details</h2>
            <table className="expense-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Amount</th>
                  <th>Category</th>
                </tr>
              </thead>
              <tbody>
                {results.ai_analysis?.items?.map((item, index) => (
                  <tr key={index}>
                    <td>{item.name}</td>
                    <td>₹{item.amount?.toFixed(2) || '0.00'}</td>
                    <td>
                      <span className={`category-badge ${getCategoryClass(item.category)}`}>
                        {item.category}
                      </span>
                    </td>
                  </tr>
                )) || []}
              </tbody>
            </table>
          </div>

          {chartData && (
            <div className="card">
              <h2 className="section-title">📈 Category Breakdown</h2>
              <div className="chart-container">
                <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
                  <div style={{ width: '300px', margin: '20px' }}>
                    <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>Pie Chart</h3>
                    <Pie data={chartData} options={{ responsive: true }} />
                  </div>
                  <div style={{ width: '300px', margin: '20px' }}>
                    <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>Bar Chart</h3>
                    <Bar 
                      data={chartData} 
                      options={{ 
                        responsive: true,
                        scales: {
                          y: {
                            beginAtZero: true
                          }
                        }
                      }} 
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="card">
            <h2 className="section-title">🔍 Extracted Text</h2>
            <div style={{ 
              background: '#f8f9fa', 
              padding: '15px', 
              borderRadius: '5px',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              whiteSpace: 'pre-wrap',
              maxHeight: '200px',
              overflow: 'auto'
            }}>
              {results.extracted_text}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
