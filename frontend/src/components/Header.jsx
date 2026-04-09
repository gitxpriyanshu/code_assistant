import { useState } from 'react';
import './Header.css';

export default function Header() {
  const [pulse, setPulse] = useState(false);

  return (
    <header className="header" id="app-header">
      <div className="header__inner">
        {/* Logo & title */}
        <div className="header__brand">
          <div
            className={`header__logo ${pulse ? 'header__logo--pulse' : ''}`}
            onMouseEnter={() => setPulse(true)}
            onAnimationEnd={() => setPulse(false)}
          >
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="url(#logo-grad)" />
              <path
                d="M10 22L16 10L22 22"
                stroke="white"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="16" cy="20" r="1.5" fill="white" />
              <defs>
                <linearGradient id="logo-grad" x1="0" y1="0" x2="32" y2="32">
                  <stop stopColor="#6c5ce7" />
                  <stop offset="1" stopColor="#00cec9" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div>
            <h1 className="header__title">Code Debugging Assistant</h1>
            <p className="header__subtitle">
              Powered by RAG + Groq Llama 3.3
            </p>
          </div>
        </div>

        {/* Status badge */}
        <div className="header__status">
          <span className="header__status-dot" />
          <span className="header__status-text">Online</span>
        </div>
      </div>
    </header>
  );
}
