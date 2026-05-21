/** Strip line and block comments so patterns like `:=` do not false-match. */
function stripComments(code) {
  return code
    .replace(/\/\/.*$/gm, '')
    .replace(/\/\*[\s\S]*?\*\//g, '');
}

/**
 * Best-effort language guess from source text.
 * Returns a value from LANGUAGES or null if uncertain.
 */
export function detectLikelyLanguage(code) {
  const src = (code || '').trim();
  if (!src) return null;

  const bare = stripComments(src);

  // Rust
  if (/\bfn\s+main\s*\(/.test(src) || /println!\s*\(/.test(src) || /\blet\s+mut\s+/.test(src)) {
    return 'rust';
  }

  // Go (use comment-stripped source for := to avoid false positives)
  if (
    /\bpackage\s+main\b/.test(src) ||
    /\bfmt\.Print/.test(src) ||
    /\bfunc\s+main\s*\(/.test(src) ||
    /\b\w+\s*:=/.test(bare)
  ) {
    return 'go';
  }

  // C++
  if (/#include\s*<.*>/.test(src) || /\bstd::/.test(src) || /\bcout\s*<</.test(src)) {
    return 'c++';
  }

  // Java
  if (
    /\bpublic\s+class\b/.test(src) ||
    /\bpublic\s+static\s+void\s+main\b/.test(src) ||
    /\bSystem\.out\.println\s*\(/.test(src)
  ) {
    return 'java';
  }

  const hasPythonImport =
    /^\s*import\s+[\w.]+/m.test(src) &&
    !/\bimport\s+.+?\s+from\s+['"]/.test(src) &&
    !/\bimport\s*[{'"]/.test(src);

  // Python (before TypeScript / JavaScript — shared syntax like `:` annotations)
  if (
    /\basync\s+def\b/.test(src) ||
    /\bdef\s+\w+\s*\(/.test(src) ||
    /\bclass\s+\w+[^({]*:/.test(src) ||
    /\belif\s+/.test(src) ||
    /\bexcept\s+/.test(src) ||
    /\bfinally\s*:/.test(src) ||
    /\bfrom\s+[\w.]+\s+import\b/.test(src) ||
    hasPythonImport ||
    /\bprint\s*\(/.test(src) ||
    /\bpass\b/.test(src) ||
    /\braise\s+/.test(src) ||
    /\bNone\b/.test(src) ||
    /\bTrue\b|\bFalse\b/.test(src) ||
    /^\s*@\w+/m.test(src)
  ) {
    return 'python';
  }

  // TypeScript (before JavaScript)
  if (
    /\binterface\s+\w+/.test(src) ||
    /\btype\s+\w+\s*=/.test(src) ||
    /\benum\s+\w+/.test(src) ||
    /:\s*(string|number|boolean|any|unknown|never|void)\b/.test(src)
  ) {
    return 'typescript';
  }

  // JavaScript / TypeScript-style JS
  if (
    /\b(const|let|var)\s/.test(src) ||
    /\bfunction\s+\w*\s*\(/.test(src) ||
    /\basync\s+function\b/.test(src) ||
    /\bclass\s+\w+/.test(src) ||
    /\bconsole\.\w+\s*\(/.test(src) ||
    /=>/.test(src) ||
    /\bimport\s+[\w*{]/.test(src) ||
    /\bimport\s+.+\s+from\s+['"]/.test(src) ||
    /\bexport\s+(default\s+)?/.test(src) ||
    /\brequire\s*\(/.test(src) ||
    /\bmodule\.exports\b/.test(src) ||
    /\bdocument\./.test(src) ||
    /\bwindow\./.test(src) ||
    /\baddEventListener\s*\(/.test(src) ||
    /\bJSON\.(parse|stringify)\b/.test(src) ||
    /\bPromise\b/.test(src) ||
    /\bawait\s+/.test(src) ||
    /\b===\b|\b!==\b/.test(src) ||
    /\bnull\b/.test(src) ||
    /\bundefined\b/.test(src)
  ) {
    return 'javascript';
  }

  return null;
}
