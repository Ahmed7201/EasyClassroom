import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { coursesApi } from '../api/courses';
import { format } from 'date-fns';
import {
    Search,
    Calendar,
    FileText,
    Archive,
    RefreshCw,
    ArrowUpDown,
    CheckCircle2,
    Clock
} from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import * as Tabs from '@radix-ui/react-tabs';

export default function Assignments() {
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState<'urgency' | 'newest'>('urgency');
    const [activeTab, setActiveTab] = useState('active');

    // Fetch all courses to get their assignments
    const { data: courses, isLoading: coursesLoading } = useQuery({
        queryKey: ['courses'],
        queryFn: coursesApi.list
    });

    // Fetch assignments for all courses
    const { data: allAssignments, isLoading: assignmentsLoading } = useQuery({
        queryKey: ['allAssignments', courses],
        queryFn: async () => {
            if (!courses) return [];
            const promises = courses.map(course =>
                coursesApi.getAssignments(course.id).then(assignments =>
                    assignments.map(a => ({ ...a, courseName: course.name }))
                )
            );
            const results = await Promise.all(promises);
            return results.flat();
        },
        enabled: !!courses
    });

    // Toggle Archive Mutation
    const toggleArchiveMutation = useMutation({
        mutationFn: ({ id, isArchived }: { id: string; isArchived: boolean }) =>
            coursesApi.toggleAssignmentState(id, isArchived),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['allAssignments'] });
        }
    });

    if (coursesLoading || assignmentsLoading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    const getUrgencyColor = (dueDate?: string) => {
        if (!dueDate) return 'text-gray-500';
        const days = Math.ceil((new Date(dueDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
        if (days < 0) return 'text-red-600';
        if (days <= 2) return 'text-red-500';
        if (days <= 5) return 'text-yellow-500';
        return 'text-green-500';
    };

    const getUrgencyEmoji = (dueDate?: string) => {
        if (!dueDate) return '📅';
        const days = Math.ceil((new Date(dueDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));
        if (days < 0) return '🔴';
        if (days <= 2) return '🔥';
        if (days <= 5) return '⚠️';
        return '🟢';
    };

    // Filter and Sort Logic
    const filteredAssignments = allAssignments?.filter(assignment => {
        const matchesSearch = assignment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            assignment.courseName?.toLowerCase().includes(searchTerm.toLowerCase());

        const isOld = assignment.dueDate &&
            (new Date().getTime() - new Date(assignment.dueDate.year, assignment.dueDate.month - 1, assignment.dueDate.day).getTime()) > (20 * 24 * 60 * 60 * 1000);

        if (activeTab === 'active') {
            return matchesSearch && !assignment.isArchived && !isOld;
        } else {
            return matchesSearch && (assignment.isArchived || isOld);
        }
    }).sort((a, b) => {
        if (sortBy === 'newest') {
            return new Date(b.creationTime).getTime() - new Date(a.creationTime).getTime();
        }
        // Sort by urgency (due date)
        const dateA = a.dueDate ? new Date(a.dueDate.year, a.dueDate.month - 1, a.dueDate.day).getTime() : Infinity;
        const dateB = b.dueDate ? new Date(b.dueDate.year, b.dueDate.month - 1, b.dueDate.day).getTime() : Infinity;
        return dateA - dateB;
    });

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Assignments</h1>
                    <p className="text-gray-500 dark:text-gray-400">Manage your tasks across all courses</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant={sortBy === 'urgency' ? 'primary' : 'outline'}
                        onClick={() => setSortBy('urgency')}
                        size="sm"
                    >
                        <Clock className="w-4 h-4 mr-2" />
                        Urgency
                    </Button>
                    <Button
                        variant={sortBy === 'newest' ? 'primary' : 'outline'}
                        onClick={() => setSortBy('newest')}
                        size="sm"
                    >
                        <ArrowUpDown className="w-4 h-4 mr-2" />
                        Newest
                    </Button>
                </div>
            </div>

            <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
                <Tabs.List className="flex border-b border-gray-200 dark:border-gray-700 mb-6">
                    <Tabs.Trigger
                        value="active"
                        className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${activeTab === 'active'
                                ? 'border-primary-600 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Active Assignments
                    </Tabs.Trigger>
                    <Tabs.Trigger
                        value="old"
                        className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${activeTab === 'old'
                                ? 'border-primary-600 text-primary-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Old & Archived
                    </Tabs.Trigger>
                </Tabs.List>

                <div className="relative mb-6">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search assignments..."
                        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <Tabs.Content value="active" className="space-y-4">
                    {filteredAssignments?.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <CheckCircle2 className="w-12 h-12 mx-auto mb-4 text-green-500" />
                            <p className="text-lg">All caught up! No active assignments.</p>
                        </div>
                    ) : (
                        filteredAssignments?.map(assignment => (
                            <AssignmentItem
                                key={assignment.id}
                                assignment={assignment}
                                getUrgencyColor={getUrgencyColor}
                                getUrgencyEmoji={getUrgencyEmoji}
                                onArchive={() => toggleArchiveMutation.mutate({ id: assignment.id, isArchived: true })}
                            />
                        ))
                    )}
                </Tabs.Content>

                <Tabs.Content value="old" className="space-y-4">
                    {filteredAssignments?.length === 0 ? (
                        <div className="text-center py-12 text-gray-500">
                            <Archive className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                            <p className="text-lg">No archived or old assignments.</p>
                        </div>
                    ) : (
                        filteredAssignments?.map(assignment => (
                            <AssignmentItem
                                key={assignment.id}
                                assignment={assignment}
                                getUrgencyColor={getUrgencyColor}
                                getUrgencyEmoji={getUrgencyEmoji}
                                onRestore={() => toggleArchiveMutation.mutate({ id: assignment.id, isArchived: false })}
                                isArchivedView
                            />
                        ))
                    )}
                </Tabs.Content>
            </Tabs.Root>
        </div>
    );
}

function AssignmentItem({ assignment, getUrgencyColor, getUrgencyEmoji, onArchive, onRestore, isArchivedView }: any) {
    const dueDate = assignment.dueDate
        ? new Date(assignment.dueDate.year, assignment.dueDate.month - 1, assignment.dueDate.day)
        : null;

    return (
        <Card className="hover:shadow-md transition-shadow">
            <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-start gap-4">
                    <div className={`p-2 rounded-full bg-gray-100 dark:bg-gray-800 ${getUrgencyColor(dueDate?.toISOString())}`}>
                        {getUrgencyEmoji(dueDate?.toISOString())}
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900 dark:text-white">{assignment.title}</h3>
                        <p className="text-sm text-gray-500">{assignment.courseName}</p>
                        <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                            {dueDate && (
                                <span className="flex items-center gap-1">
                                    <Calendar className="w-4 h-4" />
                                    Due: {format(dueDate, 'MMM d, yyyy')}
                                </span>
                            )}
                            <span className="flex items-center gap-1">
                                <FileText className="w-4 h-4" />
                                {assignment.maxPoints || 0} pts
                            </span>
                        </div>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => window.open(assignment.alternateLink, '_blank')}>
                        Open
                    </Button>
                    {isArchivedView ? (
                        <Button variant="ghost" size="sm" onClick={onRestore} title="Restore">
                            <RefreshCw className="w-4 h-4" />
                        </Button>
                    ) : (
                        <Button variant="ghost" size="sm" onClick={onArchive} title="Archive">
                            <Archive className="w-4 h-4" />
                        </Button>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
