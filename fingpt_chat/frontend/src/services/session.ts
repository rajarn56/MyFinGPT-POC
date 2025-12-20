/** Session management utilities */
const SESSION_STORAGE_KEY = 'myfingpt_session_id';
const SESSION_EXPIRY_KEY = 'myfingpt_session_expires_at';

export const sessionService = {
  getSessionId(): string | null {
    if (typeof window === 'undefined') return null;
    
    const sessionId = localStorage.getItem(SESSION_STORAGE_KEY);
    const expiresAt = localStorage.getItem(SESSION_EXPIRY_KEY);
    
    if (!sessionId || !expiresAt) {
      return null;
    }
    
    // Check if session expired
    const expiryTime = new Date(expiresAt).getTime();
    if (Date.now() > expiryTime) {
      this.clearSession();
      return null;
    }
    
    return sessionId;
  },

  saveSession(sessionId: string, expiresAt: string): void {
    if (typeof window === 'undefined') return;
    
    localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
    localStorage.setItem(SESSION_EXPIRY_KEY, expiresAt);
  },

  clearSession(): void {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem(SESSION_STORAGE_KEY);
    localStorage.removeItem(SESSION_EXPIRY_KEY);
  },
};

