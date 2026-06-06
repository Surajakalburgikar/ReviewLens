/**
 * SentimentBar Component.
 * Displays the classification confidence score using a clean, custom-styled Recharts horizontal bar.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell } from 'recharts';

export default function SentimentBar({ sentiment, confidence }) {
  // Convert confidence to percentage (0 - 100)
  const percentage = Math.round(confidence * 100);
  
  // Format data for Recharts
  const data = [
    {
      name: 'Confidence',
      value: percentage,
      displayVal: `${percentage}%`,
    }
  ];

  // Map sentiment to hex color tokens (STRICT: no blue or purple)
  const getColor = () => {
    switch (sentiment) {
      case 'Positive':
        return '#10b981'; // Emerald Green
      case 'Negative':
        return '#ef4444'; // Crimson Red
      default:
        return '#f59e0b'; // Amber Gold
    }
  };

  const activeColor = getColor();

  return (
    <div className="sentiment-bar-wrapper" style={{ marginTop: '1rem', width: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem', fontSize: '0.9rem', fontWeight: 600 }}>
        <span style={{ color: 'var(--text-secondary)' }}>Prediction Confidence</span>
        <span style={{ color: activeColor }}>{percentage}%</span>
      </div>
      
      <div style={{ width: '100%', height: 35, background: 'rgba(255, 255, 255, 0.03)', borderRadius: '4px', overflow: 'hidden', border: '1px solid var(--border-color)' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            layout="vertical"
            data={data}
            margin={{ top: 0, right: 0, left: 0, bottom: 0 }}
          >
            {/* Define horizontal X-axis mapping values from 0 to 100 */}
            <XAxis type="number" domain={[0, 100]} hide />
            {/* Define Y-axis for categorical grouping */}
            <YAxis type="category" dataKey="name" hide />
            <Bar 
              dataKey="value" 
              background={{ fill: 'transparent' }} 
              radius={[0, 4, 4, 0]}
              animationDuration={800}
            >
              <Cell fill={activeColor} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

SentimentBar.propTypes = {
  sentiment: PropTypes.oneOf(['Positive', 'Negative', 'Neutral']).isRequired,
  confidence: PropTypes.number.isRequired,
};
