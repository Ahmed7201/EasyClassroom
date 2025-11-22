import axios, { AxiosInstance, AxiosError } from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api'

export const client: AxiosInstance = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor - add auth token
client.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().token
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

// Response interceptor - handle errors and token refresh
client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config

        // Handle 401 Unauthorized - token expired
        if (error.response?.status === 401 && originalRequest) {
            try {
                // Attempt to refresh token
                const response = await axios.post(`${API_URL}/auth/refresh`)
                const { token } = response.data

                useAuthStore.getState().setAuth(useAuthStore.getState().user!, token)

                // Retry original request with new token
                originalRequest.headers.Authorization = `Bearer ${token}`
                return client(originalRequest)
            } catch (refreshError) {
                // Refresh failed - logout user
                useAuthStore.getState().logout()
                window.location.href = '/login'
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)

export default client
