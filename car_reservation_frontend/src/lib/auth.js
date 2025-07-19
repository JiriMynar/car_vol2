// Authentication utility functions

export const getStoredToken = () => {
  return localStorage.getItem('access_token');
};

export const getStoredUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const setAuthData = (token, user) => {
  localStorage.setItem('access_token', token);
  localStorage.setItem('user', JSON.stringify(user));
};

export const clearAuthData = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
};

export const isAuthenticated = () => {
  return !!getStoredToken();
};

export const isAdmin = () => {
  const user = getStoredUser();
  return user && user.role_name === 'Fleet Administrator';
};

export const canModifyReservation = (reservation, user) => {
  if (!reservation || !user) return false;
  
  // Admin can modify any reservation
  if (user.role_name === 'Fleet Administrator') return true;
  
  // User can only modify their own reservations
  if (reservation.user_id !== user.user_id) return false;
  
  // Check if reservation is still modifiable (2 hours before start)
  const startTime = new Date(reservation.start_time);
  const now = new Date();
  const hoursUntilStart = (startTime - now) / (1000 * 60 * 60);
  
  return hoursUntilStart >= 2 && reservation.status === 'Confirmed';
};

