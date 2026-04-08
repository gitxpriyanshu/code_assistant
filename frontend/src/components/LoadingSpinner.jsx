import './LoadingSpinner.css';

export default function LoadingSpinner({ message = 'Analyzing your code…' }) {
  return (
    <div className="spinner-container" id="loading-spinner">
      <div className="spinner">
        <div className="spinner__ring" />
        <div className="spinner__ring spinner__ring--inner" />
        <div className="spinner__icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L12 6M12 18L12 22M4.93 4.93L7.76 7.76M16.24 16.24L19.07 19.07M2 12H6M18 12H22M4.93 19.07L7.76 16.24M16.24 7.76L19.07 4.93"
              stroke="url(#spinner-grad)"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <defs>
              <linearGradient id="spinner-grad" x1="2" y1="2" x2="22" y2="22">
                <stop stopColor="#6c5ce7" />
                <stop offset="1" stopColor="#00cec9" />
              </linearGradient>
            </defs>
          </svg>
        </div>
      </div>
      <p className="spinner__message">{message}</p>
      <div className="spinner__dots">
        <span className="spinner__dot" />
        <span className="spinner__dot" />
        <span className="spinner__dot" />
      </div>
    </div>
  );
}
