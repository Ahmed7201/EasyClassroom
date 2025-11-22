import { client } from './client'
import { WhatsAppSettings } from '../types/models'

export const whatsappApi = {
    getSettings: async (): Promise<WhatsAppSettings> => {
        const response = await client.get<WhatsAppSettings>('/settings')
        return response.data
    },

    updateSettings: async (settings: WhatsAppSettings): Promise<WhatsAppSettings> => {
        const response = await client.put<WhatsAppSettings>('/settings', settings)
        return response.data
    },

    sendTest: async (): Promise<void> => {
        await client.post('/whatsapp/test')
    },

    sendSummary: async (): Promise<void> => {
        await client.post('/whatsapp/summary')
    }
}
