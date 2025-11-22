import { client } from './client'
import { Course, Assignment, GradeReport } from '../types/models'

export const coursesApi = {
    list: async (): Promise<Course[]> => {
        const response = await client.get<Course[]>('/courses')
        return response.data
    },

    get: async (id: string): Promise<Course> => {
        const response = await client.get<Course>(`/courses/${id}`)
        return response.data
    },

    getAssignments: async (courseId: string): Promise<Assignment[]> => {
        const response = await client.get<Assignment[]>(`/courses/${courseId}/assignments`)
        return response.data
    },

    getGrades: async (courseId: string) => {
        const response = await client.get<GradeReport>(`/courses/${courseId}/grades`);
        return response.data;
    },

    toggleAssignmentState: async (assignmentId: string, isArchived: boolean) => {
        const response = await client.patch<{ message: string; isArchived: boolean }>(
            `/assignments/${assignmentId}/state`,
            { isArchived }
        );
        return response.data;
    },
};
