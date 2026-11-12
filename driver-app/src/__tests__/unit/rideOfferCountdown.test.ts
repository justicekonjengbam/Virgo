import { calculateOfferSecondsLeft, parseOfferExpiresAtMs } from '../../features/rides/utils/offerTime';

describe('RideRequestScreen countdown and timezone parsing', () => {
  const baseTimeUtc = '2026-11-11T13:06:45.000Z';
  const nowMs = new Date(baseTimeUtc).getTime();

  it('parses naive UTC datetime string as UTC (not local IST device time)', () => {
    // 45s in the future from 13:06:45 UTC is 13:07:30 UTC
    const naiveUtcString = '2026-11-11T13:07:30.000000';
    const parsedMs = parseOfferExpiresAtMs(naiveUtcString);
    const expectedMs = new Date('2026-11-11T13:07:30.000Z').getTime();

    expect(parsedMs).toBe(expectedMs);
    expect(calculateOfferSecondsLeft(naiveUtcString, nowMs)).toBe(45);
  });

  it('parses timezone-aware UTC datetime string with trailing Z', () => {
    const awareUtcString = '2026-11-11T13:07:30.000000Z';
    const parsedMs = parseOfferExpiresAtMs(awareUtcString);
    const expectedMs = new Date('2026-11-11T13:07:30.000Z').getTime();

    expect(parsedMs).toBe(expectedMs);
    expect(calculateOfferSecondsLeft(awareUtcString, nowMs)).toBe(45);
  });

  it('parses naive datetime with space separator as UTC', () => {
    const naiveSpaceString = '2026-11-11 13:07:30.000000';
    const parsedMs = parseOfferExpiresAtMs(naiveSpaceString);
    const expectedMs = new Date('2026-11-11T13:07:30.000Z').getTime();

    expect(parsedMs).toBe(expectedMs);
    expect(calculateOfferSecondsLeft(naiveSpaceString, nowMs)).toBe(45);
  });

  it('keeps valid offer visible and tracks countdown throughout its 45-second lifetime', () => {
    const expiresAt = '2026-11-11T13:07:30.000Z';

    // At 0s elapsed: 45s remaining
    expect(calculateOfferSecondsLeft(expiresAt, nowMs)).toBe(45);

    // At 20s elapsed: 25s remaining
    expect(calculateOfferSecondsLeft(expiresAt, nowMs + 20_000)).toBe(25);

    // At 44s elapsed: 1s remaining
    expect(calculateOfferSecondsLeft(expiresAt, nowMs + 44_000)).toBe(1);

    // At 44.9s elapsed: 0s or 1s remaining (not expired prematurely)
    expect(calculateOfferSecondsLeft(expiresAt, nowMs + 44_400)).toBe(1);
  });

  it('clears an actually expired offer by returning 0 seconds left', () => {
    const expiresAt = '2026-11-11T13:07:30.000Z';

    // At exactly 45s elapsed: 0s left
    expect(calculateOfferSecondsLeft(expiresAt, nowMs + 45_000)).toBe(0);

    // After 46s elapsed: 0s left (Math.max(0, ...))
    expect(calculateOfferSecondsLeft(expiresAt, nowMs + 46_000)).toBe(0);

    // An offer from 5 minutes ago: 0s left
    const oldOffer = '2026-11-11T13:00:00.000Z';
    expect(calculateOfferSecondsLeft(oldOffer, nowMs)).toBe(0);
  });
});
