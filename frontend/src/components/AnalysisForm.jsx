/**
 * AnalysisForm Component.
 * Provides two input modes:
 *   1. Paste Text — user types/pastes review text directly
 *   2. From URL  — user enters a URL, frontend calls /scrape,
 *                  extracted text is loaded into the textarea for review
 *
 * Supported URL types:
 *   - Google Play Store: play.google.com/store/apps/details?id=...
 *   - Apple App Store: apps.apple.com/.../id...
 *   - Generic web pages: any URL with <p> tag content
 */
import React, { useState } from 'react';
import { Send, Link, FileText, Loader, AlertTriangle } from 'lucide-react';
import apiClient from '../api/axios';

export default function AnalysisForm({ onSubmit, isLoading }) {
  // Tab state: 'text' (paste mode) or 'url' (scrape mode)
  const [activeTab, setActiveTab] = useState('text');

  // Text paste mode state
  const [text, setText] = useState('');

  // URL mode state
  const [url, setUrl] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeError, setScrapeError] = useState(null);
  const [scrapeInfo, setScrapeInfo] = useState(null); // success info message

  const minLength = 20;
  const maxLength = 5000;
  const currentLength = text.trim().length;

  const isTooShort = currentLength > 0 && currentLength < minLength;
  const isTooLong = currentLength > maxLength;
  const isSubmitDisabled = currentLength < minLength || currentLength > maxLength || isLoading || isScraping;

  // Character counter colour
  const getCounterColor = () => {
    if (isTooLong) return 'var(--sentiment-negative)';
    if (isTooShort) return 'var(--sentiment-neutral)';
    if (currentLength >= minLength) return 'var(--sentiment-positive)';
    return 'var(--text-secondary)';
  };

  // Submit text for analysis
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!isSubmitDisabled) {
      onSubmit(text.trim());
    }
  };

  // Scrape reviews from URL and load into textarea
  const handleScrape = async (e) => {
    e.preventDefault();
    if (!url.trim() || isScraping) return;

    setIsScraping(true);
    setScrapeError(null);
    setScrapeInfo(null);

    try {
      const response = await apiClient.get('/scrape', {
        params: { url: url.trim() },
      });

      const { text: scrapedText, source, count, error } = response.data;

      if (error || !scrapedText) {
        // Scraping failed — show clear message
        setScrapeError(
          error || 'Could not extract any review text from this URL. Try pasting the text directly.'
        );
        return;
      }

      // Success — load extracted text into textarea and switch to text tab
      setText(scrapedText.slice(0, maxLength)); // cap at max length
      setScrapeInfo(
        `✓ Extracted ${count} review${count !== 1 ? 's' : ''} from ${
          source === 'google_play' ? 'Google Play Store' :
          source === 'app_store' ? 'Apple App Store' : 'web page'
        }. Review the text below, then click Analyze.`
      );
      setActiveTab('text'); // switch to text tab to show loaded content

    } catch (err) {
      console.error('Scrape request failed:', err);
      setScrapeError(
        'Failed to connect to the scraping service. Please check if the backend is running.'
      );
    } finally {
      setIsScraping(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>

      {/* Tab switcher */}
      <div style={{
        display: 'flex',
        gap: '0.5rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
        paddingBottom: '0',
      }}>
        <button
          type="button"
          onClick={() => setActiveTab('text')}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            padding: '0.6rem 1rem',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'text' ? '2px solid var(--accent-brand)' : '2px solid transparent',
            color: activeTab === 'text' ? 'var(--accent-brand)' : 'var(--text-secondary)',
            cursor: 'pointer',
            fontWeight: activeTab === 'text' ? '600' : '400',
            fontSize: '0.9rem',
            transition: 'all 0.15s ease',
          }}
        >
          <FileText size={15} />
          Paste Text
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('url')}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            padding: '0.6rem 1rem',
            background: 'none',
            border: 'none',
            borderBottom: activeTab === 'url' ? '2px solid var(--accent-brand)' : '2px solid transparent',
            color: activeTab === 'url' ? 'var(--accent-brand)' : 'var(--text-secondary)',
            cursor: 'pointer',
            fontWeight: activeTab === 'url' ? '600' : '400',
            fontSize: '0.9rem',
            transition: 'all 0.15s ease',
          }}
        >
          <Link size={15} />
          From URL
        </button>
      </div>

      {/* ── URL Tab ── */}
      {activeTab === 'url' && (
        <form onSubmit={handleScrape} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>

          <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: '500' }}>
            App or Review Page URL
          </label>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <input
              type="url"
              required
              value={url}
              onChange={(e) => { setUrl(e.target.value); setScrapeError(null); setScrapeInfo(null); }}
              placeholder="https://play.google.com/store/apps/details?id=com.example.app"
              disabled={isScraping}
              style={{
                flex: 1,
                padding: '0.75rem 1rem',
                background: 'var(--bg-secondary)',
                border: '1px solid rgba(255, 255, 255, 0.15)',
                borderRadius: '8px',
                color: 'var(--text-primary)',
                fontSize: '0.9rem',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={!url.trim() || isScraping}
              style={{
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                padding: '0.75rem 1.25rem',
                background: 'var(--accent-brand)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: !url.trim() || isScraping ? 'not-allowed' : 'pointer',
                opacity: !url.trim() || isScraping ? 0.6 : 1,
                fontWeight: '600',
                fontSize: '0.9rem',
                whiteSpace: 'nowrap',
              }}
            >
              {isScraping ? <Loader size={15} className="spin" /> : <Link size={15} />}
              {isScraping ? 'Fetching...' : 'Fetch Reviews'}
            </button>
            {url && (
              <button
                type="button"
                onClick={() => {
                  setUrl('');
                  setScrapeError(null);
                }}
                disabled={isScraping}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: 'none',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '8px',
                  color: 'var(--text-secondary)',
                  cursor: isScraping ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.9rem',
                  transition: 'all 0.15s ease',
                }}
              >
                Clear
              </button>
            )}
          </div>

          {/* Supported source hints */}
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0 }}>
            ✓ Google Play Store &nbsp;·&nbsp; ✓ Apple App Store &nbsp;·&nbsp; ✓ Review blogs &amp; articles
            &nbsp;·&nbsp; ✗ Amazon &amp; Flipkart (blocked)
          </p>

          {/* Scrape error */}
          {scrapeError && (
            <div style={{
              display: 'flex', alignItems: 'flex-start', gap: '0.5rem',
              padding: '0.75rem 1rem',
              background: 'rgba(239,68,68,0.08)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '8px',
              color: 'var(--sentiment-negative)',
              fontSize: '0.85rem',
            }}>
              <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: '2px' }} />
              {scrapeError}
            </div>
          )}
        </form>
      )}

      {/* ── Text Tab ── */}
      {activeTab === 'text' && (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>

          {/* Scrape success info banner — shown after URL fetch */}
          {scrapeInfo && (
            <div style={{
              padding: '0.65rem 1rem',
              background: 'rgba(16,185,129,0.08)',
              border: '1px solid rgba(16,185,129,0.3)',
              borderRadius: '8px',
              color: 'var(--sentiment-positive)',
              fontSize: '0.83rem',
            }}>
              {scrapeInfo}
            </div>
          )}

          <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: '500' }}>
            Product Review Text
          </label>

          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste product reviews here... or use the 'From URL' tab to fetch them automatically."
            rows={8}
            disabled={isLoading}
            style={{
              padding: '0.85rem 1rem',
              background: 'var(--bg-secondary)',
              border: `1px solid ${isTooLong ? 'var(--sentiment-negative)' : isTooShort ? 'var(--sentiment-neutral)' : 'rgba(255, 255, 255, 0.15)'}`,
              borderRadius: '8px',
              color: 'var(--text-primary)',
              fontSize: '0.9rem',
              lineHeight: '1.6',
              resize: 'vertical',
              outline: 'none',
              fontFamily: 'inherit',
            }}
          />

          {/* Character counter row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', color: getCounterColor() }}>
              {isTooShort && `${minLength - currentLength} more characters needed`}
              {isTooLong && `${currentLength - maxLength} characters over limit`}
              {!isTooShort && !isTooLong && currentLength > 0 && 'Ready to analyze'}
            </span>
            <span style={{ fontSize: '0.78rem', color: getCounterColor() }}>
              {currentLength.toLocaleString()} / {maxLength.toLocaleString()}
            </span>
          </div>

          {/* Submit and Clear button group */}
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              type="submit"
              disabled={isSubmitDisabled}
              style={{
                flex: 1,
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem',
                padding: '0.85rem 1.5rem',
                background: 'var(--accent-brand)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: isSubmitDisabled ? 'not-allowed' : 'pointer',
                opacity: isSubmitDisabled ? 0.55 : 1,
                fontWeight: '600',
                fontSize: '0.95rem',
                transition: 'opacity 0.15s ease',
              }}
            >
              <Send size={16} />
              {isLoading ? 'Analyzing...' : 'Analyze Review'}
            </button>

            {text && (
              <button
                type="button"
                onClick={() => {
                  setText('');
                  setScrapeInfo(null);
                }}
                disabled={isLoading}
                style={{
                  padding: '0.85rem 1.5rem',
                  background: 'none',
                  border: '1px solid rgba(255, 255, 255, 0.15)',
                  borderRadius: '8px',
                  color: 'var(--text-secondary)',
                  cursor: isLoading ? 'not-allowed' : 'pointer',
                  fontWeight: '600',
                  fontSize: '0.95rem',
                  transition: 'all 0.15s ease',
                }}
              >
                Clear
              </button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
