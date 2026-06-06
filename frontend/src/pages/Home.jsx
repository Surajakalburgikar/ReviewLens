/**
 * Home Page (Dashboard).
 * Provides the main interface where users submit review texts, view progress status,
 * and review results.
 */
import React, { useState } from 'react';
import { Sparkles, Terminal } from 'lucide-react';
import AnalysisForm from '../components/AnalysisForm';
import ResultCard from '../components/ResultCard';
import apiClient from '../api/axios';
import { getSessionId } from '../utils/session';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);

  const handleAnalyze = async (text) => {
    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    
    try {
      const session_id = getSessionId();
      
      // Send analyze request to backend
      const response = await apiClient.post('/analyze', {
        text,
        session_id,
      });

      const { data, error: apiError } = response.data;

      if (apiError) {
        setError(apiError);
      } else {
        setAnalysisResult(data);
      }
    } catch (err) {
      console.error("Analysis API request failed:", err);
      setError("Unable to connect to the analysis service. Please check if the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <Sparkles style={{ color: 'var(--accent-brand)', width: '32px', height: '32px' }} />
          <span>Review<span>Lens</span></span>
        </h1>
        <p className="subtitle">
          Unlock instant customer insights. Extract summaries, keywords, and predictive sentiment scores with explainable AI.
        </p>
      </div>

      <div className="glass-card">
        <AnalysisForm onSubmit={handleAnalyze} isLoading={isLoading} />
      </div>

      {isLoading && (
        <div className="spinner-container" style={{ animation: 'fadeIn 0.2s ease-out' }}>
          <div className="spinner"></div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500 }}>
            Training insights & calculating attributions...
          </p>
        </div>
      )}

      {error && (
        <div className="error-banner" style={{ animation: 'fadeIn 0.3s ease-out' }}>
          {error}
        </div>
      )}

      {analysisResult && (
        <ResultCard result={analysisResult} />
      )}
    </div>
  );
}
