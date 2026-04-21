import React from 'react';
import { Clock } from 'lucide-react';

export default function HistoryPanel({ history, onSelect }) {
  if (!history || history.length === 0) return null;

  return (
    <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-5 transition-colors duration-200">
      <div className="flex items-center gap-2 mb-4">
        <Clock size={16} className="text-gray-500 dark:text-gray-400" />
        <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-200">Recent Debugs</h3>
      </div>

      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto pr-1">
        {history.map((item, index) => {
          const firstLine = (item.code || '').split('\n')[0].trim();
          const preview = firstLine.length > 50 ? firstLine.substring(0, 50) + '…' : firstLine;
          const errorPreview = item.error_message
            ? item.error_message.split('\n')[0].trim().substring(0, 40)
            : null;

          return (
            <button
              key={index}
              onClick={() => onSelect(item)}
              className="w-full text-left p-3 bg-gray-50 dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-lg hover:border-blue-400 dark:hover:border-blue-600 hover:bg-blue-50 dark:hover:bg-blue-950/20 transition-colors duration-150 group"
            >
              <p className="text-xs font-mono text-gray-800 dark:text-gray-200 truncate group-hover:text-blue-700 dark:group-hover:text-blue-400">
                {preview || 'Empty code'}
              </p>
              {errorPreview && (
                <p className="text-xs text-red-500 dark:text-red-400 mt-1 truncate">
                  {errorPreview}
                </p>
              )}
              {item.explanation && (
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                  {item.explanation.substring(0, 60)}…
                </p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
