/**
 * Storage Utility Functions
 */

const TOKEN_KEY = 'dairy_access_token';
const REFRESH_TOKEN_KEY = 'dairy_refresh_token';
const USER_KEY = 'dairy_user';

export const storageUtils = {
  // Token management
  saveToken: (token) => localStorage.setItem(TOKEN_KEY, token),
  getToken: () => localStorage.getItem(TOKEN_KEY),
  removeToken: () => localStorage.removeItem(TOKEN_KEY),

  // Refresh token management
  saveRefreshToken: (token) => localStorage.setItem(REFRESH_TOKEN_KEY, token),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  removeRefreshToken: () => localStorage.removeItem(REFRESH_TOKEN_KEY),

  // User data management
  saveUser: (user) => localStorage.setItem(USER_KEY, JSON.stringify(user)),
  getUser: () => {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },
  removeUser: () => localStorage.removeItem(USER_KEY),

  // Clear all
  clear: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
};
