/**
 * KeywordChip Component.
 * Styled tags representing key phrases/topics extracted from review text.
 */
import React from 'react';
import PropTypes from 'prop-types';

export default function KeywordChip({ word }) {
  return (
    <span 
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.35rem 0.75rem',
        borderRadius: '6px',
        fontSize: '0.85rem',
        fontWeight: 500,
        backgroundColor: 'var(--bg-tertiary)',
        border: '1px solid var(--border-color)',
        color: 'var(--text-secondary)',
        marginRight: '0.5rem',
        marginBottom: '0.5rem',
        transition: 'var(--transition-smooth)',
        cursor: 'default'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--accent-brand)';
        e.currentTarget.style.color = 'var(--text-primary)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--border-color)';
        e.currentTarget.style.color = 'var(--text-secondary)';
      }}
    >
      #{word}
    </span>
  );
}

KeywordChip.propTypes = {
  word: PropTypes.string.isRequired,
};
