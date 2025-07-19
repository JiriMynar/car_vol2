import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, parseISO, isValid } from 'date-fns';
import { cs } from 'date-fns/locale';

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

// Date formatting utilities
export const formatDate = (date, formatStr = 'dd.MM.yyyy') => {
  if (!date) return '';
  
  let dateObj = date;
  if (typeof date === 'string') {
    dateObj = parseISO(date);
  }
  
  if (!isValid(dateObj)) return '';
  
  return format(dateObj, formatStr, { locale: cs });
};

export const formatDateTime = (date, formatStr = 'dd.MM.yyyy HH:mm') => {
  return formatDate(date, formatStr);
};

export const formatTime = (date, formatStr = 'HH:mm') => {
  return formatDate(date, formatStr);
};

// Form validation utilities
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateLicensePlate = (plate) => {
  // Czech license plate format: 1A2 3456 or 1AB 2345
  const plateRegex = /^[0-9][A-Z]{1,2}[0-9]\s[0-9]{3,4}$/;
  return plateRegex.test(plate);
};

// Status color utilities
export const getStatusColor = (status) => {
  const statusColors = {
    'Active': 'bg-green-100 text-green-800',
    'In Service': 'bg-yellow-100 text-yellow-800',
    'Deactivated': 'bg-gray-100 text-gray-800',
    'Archived': 'bg-red-100 text-red-800',
    'Confirmed': 'bg-blue-100 text-blue-800',
    'Cancelled': 'bg-red-100 text-red-800',
    'Completed': 'bg-green-100 text-green-800',
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Repaired': 'bg-green-100 text-green-800',
    'Irreparable': 'bg-red-100 text-red-800',
  };
  
  return statusColors[status] || 'bg-gray-100 text-gray-800';
};

// Vehicle type utilities
export const getFuelTypeIcon = (fuelType) => {
  const icons = {
    'Benzín': '⛽',
    'Nafta': '🛢️',
    'Elektřina': '🔋',
    'Hybrid': '🔋⛽',
  };
  
  return icons[fuelType] || '⛽';
};

export const getTransmissionIcon = (transmission) => {
  const icons = {
    'Manuální': '🎛️',
    'Automatická': '🔄',
  };
  
  return icons[transmission] || '🎛️';
};

// Error handling utilities
export const getErrorMessage = (error) => {
  if (error.response?.data?.error) {
    return error.response.data.error;
  }
  
  if (error.message) {
    return error.message;
  }
  
  return 'Došlo k neočekávané chybě';
};

// Calendar utilities
export const getCalendarEventColor = (event) => {
  // Different colors for different users or purposes
  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
    'bg-indigo-500',
  ];
  
  // Use user_id to determine color consistently
  const colorIndex = event.user_id % colors.length;
  return colors[colorIndex];
};

// Export utilities
export const downloadCSV = (data, filename) => {
  const csvContent = "data:text/csv;charset=utf-8," + data;
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

