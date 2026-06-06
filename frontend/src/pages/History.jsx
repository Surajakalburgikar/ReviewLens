/**
 * History Page.
 * Displays past analyses run by this user session.
 * Allows expanding history items to see the full analysis report.
 */
import React, { useEffect, useState } from 'react';
import { History as HistoryIcon, ChevronDown, ChevronUp, AlertCircle, Calendar } from 'lucide-react';
import apiClient from '../api/axios';
import { getSessionId } from '../utils/session';
import ResultCard from '../components/ResultCard';

export default function History() {
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Track which history ID is currently expanded/viewed in detail
  const [expandedId, setExpandedId] = useState(null);

  const fetchHistory = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const session_id = getSessionId();
      const response = await apiClient.get(`/history/${session_id}`);
      const { data, error: apiError } = response.data;

      if (apiError) {
        setError(apiError);
      } else {
        setHistoryItems(data || []);
      }
    } catch (err) {
      console.error("Failed to load history:", err);
      setError("Unable to connect to the history service. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'Positive': return 'var(--sentiment-positive)';
      case 'Negative': return 'var(--sentiment-negative)';
      default: return 'var(--sentiment-neutral)';
    }
  };

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}>
          <HistoryIcon style={{ color: 'var(--accent-brand)', width: '30px', height: '30px' }} />
          <span>Analysis History</span>
        </h1>
        <p className="subtitle">
          Review your recently processed review reports for this session.
        </p>
      </div>

      {isLoading && (
        <div className="spinner-container">
          <div className="spinner"></div>
          <p style={{ color: 'var(--text-secondary)' }}>Loading history records...</p>
        </div>
      )}

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {!isLoading && !error && historyItems.length === 0 && (
        <div 
          className="glass-card" 
          style={{ 
            textAlign: 'center', 
            padding: '4rem 2rem', 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            gap: '1rem',
            color: 'var(--text-secondary)'
          }}
        >
          <AlertCircle size={48} style={{ color: 'var(--text-muted)' }} />
          <div>
            <h3 style={{ color: 'var(--text-primary)', marginBottom: '0.25rem' }}>No History Yet</h3>
            <p style={{ fontSize: '0.95rem' }}>Your past sentiment predictions and summaries will appear here.</p>
          </div>
        </div>
      )}

      {!isLoading && !error && historyItems.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {historyItems.map((item) => {
            const isExpanded = expandedId === item.id;
            const dateStr = new Date(item.created_at).toLocaleDateString(undefined, {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            });

            return (
              <div key={item.id} style={{ display: 'flex', flexDirection: 'column' }}>
                {/* Accordion header card */}
                <div 
                  className="glass-card"
                  onClick={() => toggleExpand(item.id)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '1.25rem 1.5rem',
                    margin: 0,
                    cursor: 'pointer',
                    borderRadius: isExpanded ? '12px 12px 0 0' : '12px',
                    backgroundColor: isExpanded ? 'rgba(255, 255, 255, 0.02)' : 'var(--bg-secondary)',
                    borderBottom: isExpanded ? 'none' : '1px solid var(--border-color)',
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', width: '75%' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                      <span 
                        style={{ 
                          fontSize: '0.85rem', 
                          fontWeight: 700, 
                          color: getSentimentColor(item.sentiment),
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em'
                        }}
                      >
                        {item.sentiment} ({Math.round(item.confidence * 100)}%)
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        <Calendar size={12} />
                        <span>{dateStr}</span>
                      </span>
                    </div>
                    
                    <p 
                      style={{ 
                        fontSize: '0.9rem', 
                        color: 'var(--text-secondary)',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        marginTop: '0.25rem'
                      }}
                    >
                      {item.original_text}
                    </p>
                  </div>

                  <div style={{ color: 'var(--text-secondary)' }}>
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                  </div>
                </div>

                {/* Expanded details container */}
                {isExpanded && (
                  <div 
                    style={{ 
                      marginTop: -1,
                      border: '1px solid var(--border-color)',
                      borderTop: 'none',
                      borderRadius: '0 0 12px 12px',
                      overflow: 'hidden',
                      backgroundColor: 'rgba(255, 255, 255, 0.005)',
                      padding: '0 1rem 1rem 1rem',
                      marginBottom: '1rem'
                    }}
                  >
                    {/* Render the full results component within the accordion */}
                    <ResultCard result={item} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
