import React from 'react';

/**
 * Background Component
 * Renders a stable, high-performance background layer.
 * Memoized to prevent re-renders when the parent App state changes.
 */
const Background = React.memo(() => {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none select-none">
      <img
        src="https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=2070"
        className="w-full h-full object-cover opacity-10 grayscale"
        alt=""
      />
    </div>
  );
});

Background.displayName = 'Background';

export default Background;
