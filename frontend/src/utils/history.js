const MAX_HISTORY = 5;
const STORAGE_KEY = 'debug_history';

export function getHistory() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch {
    return [];
  }
}

export function saveToHistory(entry) {
  const history = getHistory();
  const filtered = history.filter((h) => h.code !== entry.code);
  const updated = [entry, ...filtered].slice(0, MAX_HISTORY);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  return updated;
}
