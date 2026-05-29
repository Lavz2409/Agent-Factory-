javascript
// client/src/utils/api.js

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

/**
 * Helper function to make GET requests to the API.
 * @param {string} endpoint - The API endpoint to send the request to.
 * @param {object} [options] - Optional fetch options.
 * @returns {Promise<any>} - The response data.
 */
export async function getRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('GET request failed:', error);
    throw error;
  }
}

/**
 * Helper function to make POST requests to the API.
 * @param {string} endpoint - The API endpoint to send the request to.
 * @param {object} data - The data to send in the request body.
 * @param {object} [options] - Optional fetch options.
 * @returns {Promise<any>} - The response data.
 */
export async function postRequest(endpoint, data, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('POST request failed:', error);
    throw error;
  }
}

/**
 * Helper function to make PUT requests to the API.
 * @param {string} endpoint - The API endpoint to send the request to.
 * @param {object} data - The data to send in the request body.
 * @param {object} [options] - Optional fetch options.
 * @returns {Promise<any>} - The response data.
 */
export async function putRequest(endpoint, data, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('PUT request failed:', error);
    throw error;
  }
}

/**
 * Helper function to make DELETE requests to the API.
 * @param {string} endpoint - The API endpoint to send the request to.
 * @param {object} [options] - Optional fetch options.
 * @returns {Promise<any>} - The response data.
 */
export async function deleteRequest(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('DELETE request failed:', error);
    throw error;
  }
}