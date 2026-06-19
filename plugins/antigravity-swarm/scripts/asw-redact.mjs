const SECRET_PATTERNS = [
  [/\bBearer\s+[A-Za-z0-9._~+/=-]{8,}/gi, "Bearer [REDACTED_TOKEN]"],
  [/\bgithub_pat_[A-Za-z0-9_]{16,}/g, "[REDACTED_TOKEN]"],
  [/\bgh[pousr]_[A-Za-z0-9_]{16,}/g, "[REDACTED_TOKEN]"],
  [/\bxox[baprs]-[A-Za-z0-9-]{10,}/g, "[REDACTED_TOKEN]"],
  [/\bsk-[A-Za-z0-9_-]{12,}/g, "[REDACTED_TOKEN]"],
  [/\b(password|passwd|token|secret|api[_-]?key|access[_-]?token|refresh[_-]?token)\b\s*([:=])\s*(['"]?)[^\s'"`]+\3/gi, "$1$2[REDACTED]"],
];

export function redactSecrets(value) {
  let text = String(value ?? "");
  for (const [pattern, replacement] of SECRET_PATTERNS) text = text.replace(pattern, replacement);
  return text;
}

export function safeMode(payload = {}) {
  return /^(1|true|yes)$/i.test(String(process.env.ASW_SAFE_MODE ?? ""))
    || payload.aswSafeMode === true
    || payload.safeMode === true
    || payload.settings?.aswSafeMode === true
    || payload.settings?.safeMode === true;
}
