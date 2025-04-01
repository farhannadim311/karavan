// src/api.js
import axios from "axios";

const API_URL = "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const signup = async (email, password) => {
  try {
    const response = await api.post("/signup", { email, password });
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
    }
    return response;
  } catch (error) {
    console.error("Signup error:", error);
    throw error;
  }
};

export const login = async (email, password) => {
  try {
    const response = await api.post("/login", { email, password });
    if (response.data.token) {
      localStorage.setItem("token", response.data.token);
      localStorage.setItem("userId", response.data.user.id);
    }
    return response;
  } catch (error) {
    console.error("Login error:", error);
    throw error;
  }
};

// Preferences
export const updatePreferences = async (userId, preferences) => {
  try {
    const response = await api.post("/preferences", {
      user_id: userId,
      ...preferences,
    });
    return response;
  } catch (error) {
    console.error("Update preferences error:", error);
    throw error;
  }
};

// Reviews
export const postReview = async (userId, campsiteName, rating, reviewText) => {
  try {
    const response = await api.post("/review", {
      user_id: userId,
      campsite_name: campsiteName,
      rating,
      review_text: reviewText,
    });
    return response;
  } catch (error) {
    console.error("Post review error:", error);
    throw error;
  }
};

export const getReviews = async (campsiteName) => {
  try {
    const response = await api.get(`/reviews/${campsiteName}`);
    return response;
  } catch (error) {
    console.error("Get reviews error:", error);
    throw error;
  }
};

// Recommendations
export const getRecommendations = async (userId, coordinates) => {
  try {
    if (!userId) {
      throw new Error("User ID is required");
    }

    if (!coordinates || !coordinates.lat || !coordinates.lng) {
      throw new Error("Valid coordinates are required");
    }

    console.log("Sending coordinates to API:", coordinates);
    const response = await api.post("/recommendations", {
      user_id: userId,
      lat: coordinates.lat,
      lng: coordinates.lng
    });
    
    console.log("API Response:", response.data);
    
    // Check if the response has the expected structure
    if (!response.data || !response.data.recommendations) {
      console.error("Invalid response structure:", response.data);
      throw new Error("Invalid response from server");
    }
    
    return response;
  } catch (error) {
    console.error("API Error:", error);
    if (error.response?.status === 400) {
      throw new Error(error.response.data.error || "Invalid request");
    } else if (error.response?.status === 404) {
      throw new Error("User not found");
    } else if (error.response?.status === 500) {
      throw new Error("Server error occurred");
    } else if (error.code === "ERR_NETWORK") {
      throw new Error("Network error: Could not connect to server");
    }
    throw error;
  }
};
