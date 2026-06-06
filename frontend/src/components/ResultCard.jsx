/**
 * ResultCard Component.
 * Displays the complete analysis report: sentiment badges, confidence charts,
 * extractive summaries, keyword tags, XAI feature importance bars, and text stats.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { FileText, Tags, Info, Eye, Clock, BarChart2 } from 'lucide-react';
import SentimentBar from './SentimentBar';
import KeywordChip from './KeywordChip';

export default function ResultCard({ result }) {
  const {
    sentiment,
    confidence,
    summary,
    keywords,
    top_influential_words,
    word_count,
    sentence_count,
    reading_time_seconds,
    created_at
  } = result;

  // Format creation date
  const formattedDate = new Date(created_at).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });

  // Get sentiment badge class and display label
  const getSentimentBadge = () => {
    switch (sentiment) {
      case 'Positive':
        return <span className="badge badge-positive">Positive Sentiment</span>;
      case 'Negative':
        return <span className="badge badge-negative">Negative Sentiment</span>;
      default:
        return <span className="badge badge-neutral">Neutral Sentiment</span>;
    }
  };

  return (
    <div className="glass-card" style={{ marginTop: '2.5rem', animation: 'fadeIn 0.4s ease-out' }}>
      {/* 1. Header Section */}
      <div 
        style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '1.25rem',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}
      >
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>Analysis Report</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>ID: {result.id}</p>
        </div>
        {getSentimentBadge()}
      </div>

      {/* 2. Confidence Metrics (Recharts) */}
      <div style={{ marginBottom: '2rem' }}>
        <SentimentBar sentiment={sentiment} confidence={confidence} />
      </div>

      {/* 3. Extractive Summary */}
      <div style={{ marginBottom: '2rem' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
          <FileText size={16} style={{ color: 'var(--accent-brand)' }} />
          <span>Extractive Text Summary</span>
        </h4>
        <div 
          style={{ 
            backgroundColor: 'var(--bg-tertiary)', 
            borderLeft: '3px solid var(--accent-brand)', 
            borderRadius: '4px',
            padding: '1.25rem',
            fontStyle: 'italic',
            color: 'var(--text-primary)',
            fontSize: '0.975rem',
            lineHeight: '1.6'
          }}
        >
          "{summary}"
        </div>
      </div>

      {/* 4. Keyword chips */}
      <div style={{ marginBottom: '2rem' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-primary)' }}>
          <Tags size={16} style={{ color: 'var(--accent-brand)' }} />
          <span>Extracted Keywords</span>
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap' }}>
          {keywords && keywords.length > 0 ? (
            keywords.map((word, idx) => <KeywordChip key={idx} word={word} />)
          ) : (
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>No keywords extracted.</span>
          )}
        </div>
      </div>

      {/* 5. Explainable AI (XAI) Section */}
      <div style={{ marginBottom: '2rem', padding: '1.25rem', backgroundColor: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '8px' }}>
        <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          <Info size={16} style={{ color: 'var(--accent-brand)' }} />
          <span>Model Explanation (Explainable AI)</span>
        </h4>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
          Below are the terms in your text that most heavily influenced the model's decision to classify this review as <strong>{sentiment}</strong>.
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {top_influential_words && top_influential_words.length > 0 ? (
            top_influential_words.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.9rem' }}>
                <span style={{ width: '110px', fontWeight: 600, color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {item.word}
                </span>
                
                <div style={{ flex: 1, height: '8px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '9999px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${item.score * 100}%`, 
                      height: '100%', 
                      backgroundColor: 'var(--accent-brand)', 
                      borderRadius: '9999px',
                      transition: 'width 0.8s ease-out'
                    }} 
                  />
                </div>
                
                <span style={{ width: '40px', textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
                  {Math.round(item.score * 100)}%
                </span>
              </div>
            ))
          ) : (
            <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              No vocabulary terms matched. Add more descriptive sentiment words.
            </span>
          )}
        </div>
      </div>

      {/* 6. Readability & Count Stats */}
      <div 
        style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(3, 1fr)', 
          gap: '1rem', 
          borderTop: '1px solid var(--border-color)',
          paddingTop: '1.25rem',
          marginBottom: '1rem',
          textAlign: 'center'
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Eye size={16} style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }} />
          <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{word_count}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Words</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <BarChart2 size={16} style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }} />
          <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{sentence_count}</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Sentences</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <Clock size={16} style={{ color: 'var(--text-secondary)', marginBottom: '0.25rem' }} />
          <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{reading_time_seconds}s</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Reading Time</span>
        </div>
      </div>

      {/* 7. Footer timestamp */}
      <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        Analyzed at {formattedDate}
      </div>
    </div>
  );
}

ResultCard.propTypes = {
  result: PropTypes.shape({
    id: PropTypes.string.isRequired,
    sentiment: PropTypes.string.isRequired,
    confidence: PropTypes.number.isRequired,
    summary: PropTypes.string.isRequired,
    keywords: PropTypes.arrayOf(PropTypes.string).isRequired,
    top_influential_words: PropTypes.arrayOf(
      PropTypes.shape({
        word: PropTypes.string.isRequired,
        score: PropTypes.number.isRequired,
      })
    ).isRequired,
    word_count: PropTypes.number.isRequired,
    sentence_count: PropTypes.number.isRequired,
    reading_time_seconds: PropTypes.number.isRequired,
    created_at: PropTypes.string.isRequired,
  }).isRequired,
};
