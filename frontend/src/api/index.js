import axios from 'axios';

const API_BASE_URL = 'http://localhost';

const AUTH_SERVICE = `${API_BASE_URL}:8001`;
const BACKUP_SERVICE = `${API_BASE_URL}:8002`;
const CONFIG_SERVICE = `${API_BASE_URL}:8003`;
const ALERT_SERVICE = `${API_BASE_URL}:8004`;
const MONITOR_SERVICE = `${API_BASE_URL}:8005`;

const getToken = () => localStorage.getItem('token');

const getAuthHeaders = () => ({
  headers: {
    'Authorization': `Bearer ${getToken()}`
  }
});

export const register = async (username, email, password) => {
  const response = await axios.post(`${AUTH_SERVICE}/register`, {
    username,
    email,
    password
  });
  return response.data;
};

export const login = async (email, password) => {
  const response = await axios.post(`${AUTH_SERVICE}/login`, {
    email,
    password
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await axios.get(`${AUTH_SERVICE}/me`, getAuthHeaders());
  return response.data;
};

export const uploadFile = async (file, provider = 's3') => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await axios.post(
    `${BACKUP_SERVICE}/upload?provider=${provider}`,
    formData,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'multipart/form-data'
      }
    }
  );
  return response.data;
};

export const listFiles = async (provider = 's3') => {
  const response = await axios.get(
    `${BACKUP_SERVICE}/list?provider=${provider}`,
    getAuthHeaders()
  );
  return response.data;
};

export const downloadFile = async (filename, provider = 's3') => {
  const response = await axios.get(
    `${BACKUP_SERVICE}/download/${filename}?provider=${provider}`,
    {
      ...getAuthHeaders(),
      responseType: 'blob'
    }
  );
  return response.data;
};

export const deleteFile = async (filename, provider = 's3') => {
  const response = await axios.delete(
    `${BACKUP_SERVICE}/delete/${filename}?provider=${provider}`,
    getAuthHeaders()
  );
  return response.data;
};

export const getConfig = async () => {
  const response = await axios.get(`${CONFIG_SERVICE}/config`, getAuthHeaders());
  return response.data;
};

export const createConfig = async (config) => {
  const response = await axios.post(`${CONFIG_SERVICE}/config`, config, getAuthHeaders());
  return response.data;
};

export const updateConfig = async (config) => {
  const response = await axios.put(`${CONFIG_SERVICE}/config`, config, getAuthHeaders());
  return response.data;
};

export const sendEmail = async (toEmail, subject, body) => {
  const response = await axios.post(
    `${ALERT_SERVICE}/send-email`,
    { to_email: toEmail, subject, body },
    getAuthHeaders()
  );
  return response.data;
};

export const sendTelegram = async (message, chatId) => {
  const response = await axios.post(
    `${ALERT_SERVICE}/send-telegram`,
    { message, chat_id: chatId },
    getAuthHeaders()
  );
  return response.data;
};

export const getHealth = async () => {
  const response = await axios.get(`${MONITOR_SERVICE}/health`);
  return response.data;
};

export const getLogs = async (limit = 100, service = null) => {
  let url = `${MONITOR_SERVICE}/logs?limit=${limit}`;
  if (service) {
    url += `&service=${service}`;
  }
  const response = await axios.get(url, getAuthHeaders());
  return response.data;
};

export const getMetricsSnapshot = async () => {
  const response = await axios.get(`${MONITOR_SERVICE}/metrics/snapshot`, getAuthHeaders());
  return response.data;
};

