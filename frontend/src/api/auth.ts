import { client } from './client'
import { User } from '../types/models'

export const authApi = {
    login: async (): Promise<void> => {
        // Redirect to Google OAuth login
        window.location.href = `${client.defaults.baseURL}/auth/google/login`
    },

    logout: async (): Promise<void> => {
        // In a real app, call backend to invalidate token
        // await client.post('/auth/logout')
    },

    getProfile: async (): Promise<User> => {
        const response = await client.get<User>('/auth/profile')
        return response.data
    },
}
