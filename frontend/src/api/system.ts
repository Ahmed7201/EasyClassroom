import { client } from './client'

export const systemApi = {
    open: async (filePath: string): Promise<void> => {
        await client.post('/system/open', { filePath })
    },
}
