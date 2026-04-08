import { useState } from 'react';
import './ResultPanel.css';

const TABS = [
  { id: 'explanation', label: 'Explanation', icon: '💡' },
  { id: 'fix', label: 'Fixed Code', icon: '🔧' },
  { id: 'optimized', label: 'Optimized', icon: '⚡' },
  { id: 'context', label: 'Context', icon: '📚' },
];

export default function ResultPanel({ result }) {
  const [activeTab, setActiveTab] = useState('explanation');
  const [copiedTab, setCopiedTab] = useState(null);

  if (!result) {
    return (
      <div className="result-panel result-panel--empty" id="result-panel">
        <div className="result-panel__empty-state">
          <div className="result-panel__empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20V4M5 11l7-7 7 7" />
            </svg>
          </div>
          <h3 className="result-panel__empty-title">Ready to Debug</h3>
          <p className="result-panel__empty-desc">
            Paste your code and error on the left, then hit <strong>Debug My Code</strong> to get
            an AI-powered explanation, fix, and optimization.
          </p>
        </div>
      </div>
    );
  }

  const handleCopy = async (text, tab) => {
    await navigator.clipboard.writeText(text);
    setCopiedTab(tab);
    setTimeout(() => setCopiedTab(null), 2000);
  };

  const getContent = () => {
    switch (activeTab) {
      case 'explanation':
        return result.explanation;
      case 'fix':
        return result.fix;
      case 'optimized':
        return result.optimized_code;
      case 'context':
        return result.relevant_context?.length
          ? result.relevant_context.join('\n\n---\n\n')
          : 'No relevant context was retrieved.';
      default:
        return '';
    }
  };

  const content = getContent();
  const isCode = activeTab === 'fix' || activeTab === 'optimized';

  return (
    <div className="result-panel" id="result-panel">
      {/* Tabs */}
      <div className="result-panel__tabs" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`result-panel__tab ${activeTab === tab.id ? 'result-panel__tab--active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="result-panel__tab-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="result-panel__content">
        <div className="result-panel__toolbar">
          <span className="result-panel__toolbar-label">
            {TABS.find((t) => t.id === activeTab)?.label}
          </span>
          <button
            className="result-panel__copy-btn"
            onClick={() => handleCopy(content, activeTab)}
          >
            {copiedTab === activeTab ? (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
                Copied!
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                Copy
              </>
            )}
          </button>
        </div>

        <div className={`result-panel__body ${isCode ? 'result-panel__body--code' : ''}`}>
          {isCode ? (
            <pre className="result-panel__code">
              <code>{content}</code>
            </pre>
          ) : (
            <div className="result-panel__text">{content}</div>
          )}
        </div>
      </div>
    </div>
  );
}
