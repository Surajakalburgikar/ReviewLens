/**
 * Session utilities for ReviewLens.
 * Manages unique, anonymous session IDs in localStorage to group past analyses.
 */

/**
 * Retrieves the persisted session UUID from localStorage.
 * If none exists, generates a new UUID, saves it, and returns it.
 * Includes a robust fallback in case crypto.randomUUID is unavailable in HTTP/legacy environments.
 */
export function getSessionId() {
  let id = localStorage.getItem('reviewlens_session_id');
  if (!id) {
    try {
      if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
        id = crypto.randomUUID();
      } else {
        // Fallback standard RFC4122 v4 UUID generator
        id = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
          const r = (Math.random() * 16) | 0;
          const v = c === 'x' ? r : (r & 0x3) | 0x8;
          return v.toString(16);
        });
      }
      localStorage.setItem('reviewlens_session_id', id);
    } catch (e) {
      console.error("Failed to generate or store session ID, falling back to temporary ID:", e);
      // Absolute fallback if localStorage is disabled
      return 'temp-session-' + Date.now();
    }
  }
  return id;
}
