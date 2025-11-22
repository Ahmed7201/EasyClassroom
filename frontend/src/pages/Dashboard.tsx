import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { coursesApi } from '../api/courses';
import { useNavigate } from 'react-router-dom';
import {
    Search,
    BookOpen,
    Users,
    MoreVertical,
    GraduationCap
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export default function Dashboard() {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');

    const { data: courses, isLoading } = useQuery({
        queryKey: ['courses'],
        queryFn: coursesApi.list
    });

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const filteredCourses = courses?.filter(course =>
        course.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Courses</h1>
                    <p className="text-gray-500 dark:text-gray-400">Access your classroom materials and assignments</p>
                </div>
            </div>

            <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                    type="text"
                    placeholder="Search courses..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredCourses?.map(course => (
                    <Card
                        key={course.id}
                        className="hover:shadow-lg transition-all cursor-pointer group border-l-4 border-l-primary-500"
                        onClick={() => navigate(`/course/${course.id}`)}
                    >
                        <CardHeader className="pb-2">
                            <div className="flex justify-between items-start">
                                <CardTitle className="text-xl font-bold text-gray-900 dark:text-white line-clamp-2 group-hover:text-primary-600 transition-colors">
                                    {course.name}
                                </CardTitle>
                                <Button variant="ghost" size="icon" className="text-gray-400 hover:text-gray-600">
                                    <MoreVertical className="w-5 h-5" />
                                </Button>
                            </div>
                            {course.section && (
                                <p className="text-sm text-gray-500 dark:text-gray-400">{course.section}</p>
                            )}
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 mb-2">
                                <GraduationCap className="w-4 h-4" />
                                <span>{course.descriptionHeading || 'General Course'}</span>
                            </div>
                            {course.room && (
                                <div className="flex items-center gap-2 text-sm text-gray-500">
                                    <Users className="w-4 h-4" />
                                    <span>Room: {course.room}</span>
                                </div>
                            )}
                        </CardContent>
                        <CardFooter className="pt-2 border-t border-gray-100 dark:border-gray-700 flex justify-between items-center">
                            <span className="text-xs font-medium px-2 py-1 bg-primary-50 text-primary-700 rounded-full dark:bg-primary-900/20 dark:text-primary-400">
                                {course.courseState}
                            </span>
                            <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-700 hover:bg-primary-50 dark:hover:bg-primary-900/20">
                                View Course →
                            </Button>
                        </CardFooter>
                    </Card>
                ))}
            </div>

            {filteredCourses?.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <p className="text-lg">No courses found matching your search.</p>
                </div>
            )}
        </div>
    );
}
