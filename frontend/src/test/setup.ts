import '@testing-library/jest-dom';

// Mock scrollIntoView for jsdom
window.HTMLElement.prototype.scrollIntoView = function () {};

// Mock crypto.randomUUID if not present
if (!globalThis.crypto) {
  // @ts-expect-error mock crypto
  globalThis.crypto = {};
}
if (!globalThis.crypto.randomUUID) {
  globalThis.crypto.randomUUID = () => '12345678-1234-1234-1234-123456789abc' as `${string}-${string}-${string}-${string}-${string}`;
}
