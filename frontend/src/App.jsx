/**
 * App Component.
 * Root layout rendering the responsive navbar, active tab view (Home/History), and the footer.
 * Implements a lightweight, state-driven router for high performance.
 */
import React, { useState } from 'react';
import { Sparkles, History as HistoryIcon, Info } from 'lucide-react';
import Home from './pages/Home';
import History from './pages/History';

export default function App() {
  // Simple state router: 'home' | 'history'
  const [activeTab, setActiveTab] = useState('home');

  return (
    <div className="app-container">
      {/* Navbar Layout */}
      <header className="navbar">
        <a 
          href="#" 
          className="logo"
          onClick={(e) => {
            e.preventDefault();
            setActiveTab('home');
          }}
        >
          <Sparkles size={20} style={{ color: 'var(--accent-brand)' }} />
          <span>Review<span>Lens</span></span>
        </a>
        
        <nav className="nav-links">
          <button
            onClick={() => setActiveTab('home')}
            className={`nav-link ${activeTab === 'home' ? 'active' : ''}`}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit' }}
          >
            Dashboard
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`nav-link ${activeTab === 'history' ? 'active' : ''}`}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
          >
            <HistoryIcon size={14} />
            <span>History</span>
          </button>
        </nav>
      </header>

      {/* Main View Area */}
      <main className="main-content">
        {activeTab === 'home' ? <Home /> : <History />}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.35rem' }}>
          <span>© {new Date().getFullYear()} ReviewLens. All rights reserved.</span>
        </div>
      </footer>
    </div>
  );
}
