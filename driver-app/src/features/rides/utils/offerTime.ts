export function parseOfferExpiresAtMs(expiresAt: string): number {
  const normalized = expiresAt.trim().replace(' ', 'T');
  const iso = normalized.endsWith('Z') || normalized.includes('+') ? normalized : `${normalized}Z`;
  return new Date(iso).getTime();
}

export function calculateOfferSecondsLeft(expiresAt: string, nowMs: number = Date.now()): number {
  const exp = parseOfferExpiresAtMs(expiresAt);
  return Math.max(0, Math.round((exp - nowMs) / 1000));
}

