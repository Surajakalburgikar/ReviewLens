/**
 * AnalysisForm Component.
 * Form input area for pasting reviews, with live validation constraints.
 */
import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Send, AlertTriangle } from 'lucide-react';

export default function AnalysisForm({ onSubmit, isLoading }) {
  const [text, setText] = useState('');
  
  const minLength = 20;
  const maxLength = 5000;
  const currentLength = text.trim().length;
  
  // Validation status
  const isTooShort = currentLength > 0 && currentLength < minLength;
  const isTooLong = currentLength > maxLength;
  const isSubmitDisabled = currentLength < minLength || currentLength > maxLength || isLoading;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isSubmitDisabled) {
      onSubmit(text);
    }
  };

  // Live status character count color helper
  const getCounterColor = () => {
    if (isTooLong) return 'var(--sentiment-negative)';
    if (isTooShort) return 'var(--sentiment-neutral)';
    if (currentLength >= minLength) return 'var(--sentiment-positive)';
    return 'var(--text-secondary)';
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="textarea-group">
        <label 
          htmlFor="review-input" 
          style={{ 
            fontSize: '0.95rem', 
            fontWeight: 600, 
            color: 'var(--text-secondary)',
            marginBottom: '0.25rem'
          }}
        >
          Product Review Text
        </label>
        
        <textarea
          id="review-input"
          className="textarea-input"
          placeholder="Paste your product reviews or text here (e.g. Amazon reviews, customer comments)..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={isLoading}
        />
        
        <div className="textarea-meta">
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: isTooShort || isTooLong ? 'var(--sentiment-neutral)' : 'var(--text-secondary)' }}>
            {isTooShort && (
              <>
                <AlertTriangle size={14} style={{ color: 'var(--sentiment-neutral)' }} />
                <span>Needs at least {minLength - currentLength} more characters.</span>
              </>
            )}
            {isTooLong && (
              <>
                <AlertTriangle size={14} style={{ color: 'var(--sentiment-negative)' }} />
                <span style={{ color: 'var(--sentiment-negative)' }}>Exceeds maximum limit by {currentLength - maxLength} characters.</span>
              </>
            )}
            {!isTooShort && !isTooLong && currentLength > 0 && (
              <span style={{ color: 'var(--sentiment-positive)' }}>✓ Meets length requirements</span>
            )}
          </span>
          
          <span style={{ fontWeight: 600, color: getCounterColor() }}>
            {currentLength} / {maxLength}
          </span>
        </div>
      </div>
      
      <button 
        type="submit" 
        className="btn btn-primary" 
        disabled={isSubmitDisabled}
        style={{ alignSelf: 'flex-end', minWidth: '140px', padding: '0.85rem 1.75rem' }}
      >
        {isLoading ? (
          <span>Analyzing...</span>
        ) : (
          <>
            <span>Analyze Sentiment</span>
            <Send size={16} />
          </>
        )}
      </button>
    </form>
  );
}

AnalysisForm.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool.isRequired,
};
