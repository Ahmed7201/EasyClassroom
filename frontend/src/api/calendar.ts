import { client } from './client'
// import { Event } from '../types/models' // Assuming Event type exists

export const calendarApi = {
    listEvents: async (): Promise<any[]> => {
        const response = await client.get('/calendar/events')
        return response.data
    },

    syncAssignments: async (): Promise<void> => {
        await client.post('/calendar/sync')
    },
}
