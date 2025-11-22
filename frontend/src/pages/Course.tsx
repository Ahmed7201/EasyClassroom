import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ExternalLink, Download, FileText } from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs'
import { Card, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Course as CourseType, Assignment, GradeReport } from '../types/models'
import { coursesApi } from '../api/courses'
import { systemApi } from '../api/system'

export default function Course() {
    const { id } = useParams<{ id: string }>()
    const [course, setCourse] = useState<CourseType | null>(null)
    const [assignments, setAssignments] = useState<Assignment[]>([])
    const [grades, setGrades] = useState<GradeReport | null>(null)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchCourseData = async () => {
            if (!id) return
            try {
                const [courseData, assignmentsData, gradesData] = await Promise.all([
                    coursesApi.get(id),
                    coursesApi.getAssignments(id),
                    coursesApi.getGrades(id)
                ])

                // Sort assignments by urgency
                assignmentsData.sort((a, b) => {
                    if (!a.deadline) return 1
                    if (!b.deadline) return -1
                    return new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
                })

                setCourse(courseData)
                setAssignments(assignmentsData)
                setGrades(gradesData)
            } catch (error) {
                console.error('Failed to fetch course data:', error)
            } finally {
                setIsLoading(false)
            }
        }

        fetchCourseData()
    }, [id])

    const handleOpenWith = async (url: string) => {
        try {
            await systemApi.open(url)
        } catch (error) {
            console.error('Failed to open system file:', error)
        }
    }

    const getUrgencyColor = (deadline: string | undefined) => {
        if (!deadline) return 'text-text/60'
        const daysLeft = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        if (daysLeft < 0) return 'text-red-500'
        if (daysLeft <= 2) return 'text-red-400'
        if (daysLeft <= 5) return 'text-orange-400'
        if (daysLeft <= 7) return 'text-yellow-400'
        return 'text-green-400'
    }

    const getUrgencyEmoji = (deadline: string | undefined) => {
        if (!deadline) return '📝'
        const daysLeft = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        if (daysLeft < 0) return '❌'
        if (daysLeft <= 2) return '🔴'
        if (daysLeft <= 5) return '🟠'
        if (daysLeft <= 7) return '🟡'
        return '🟢'
    }

    const getDaysLeft = (deadline: string | undefined) => {
        if (!deadline) return 'No deadline'
        const daysLeft = Math.ceil((new Date(deadline).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
        if (daysLeft < 0) return `Overdue by ${Math.abs(daysLeft)} days`
        if (daysLeft === 0) return 'Due today!'
        if (daysLeft === 1) return 'Due tomorrow'
        return `${daysLeft} days left`
    }

    const getTypeEmoji = (type: string | undefined) => {
        switch (type) {
            case 'EXAM': return '📝'
            case 'QUIZ': return '❓'
            case 'LAB': return '🧪'
            case 'PROJECT': return '💼'
            case 'MIDTERM': return '📚'
            case 'FINAL': return '🎓'
            default: return '📄'
        }
    }

    if (isLoading) {
        return <div className="p-8 text-center">Loading course details...</div>
    }

    if (!course) {
        return <div className="p-8 text-center">Course not found</div>
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <Link to="/" className="text-sm text-primary hover:underline mb-4 inline-block">
                    ← Back to Dashboard
                </Link>
                <div className="bg-gradient-to-r from-primary/20 to-secondary/20 rounded-xl p-8 border border-white/10">
                    <h1 className="text-4xl font-bold mb-2">{course.name}</h1>
                    <p className="text-xl text-text/80 mb-4">{course.section} • {course.room}</p>
                    {course.descriptionHeading && (
                        <h2 className="text-lg font-semibold mb-2">{course.descriptionHeading}</h2>
                    )}
                    {course.description && (
                        <p className="text-text/70 max-w-3xl">{course.description}</p>
                    )}
                </div>
            </div>

            <Tabs defaultValue="assignments" className="w-full">
                <TabsList className="mb-8 w-full justify-start bg-surface/30 p-1 border border-white/10">
                    <TabsTrigger value="assignments" className="flex-1 md:flex-none px-8">Assignments</TabsTrigger>
                    <TabsTrigger value="materials" className="flex-1 md:flex-none px-8">Materials</TabsTrigger>
                    <TabsTrigger value="grades" className="flex-1 md:flex-none px-8">Grades</TabsTrigger>
                    <TabsTrigger value="people" className="flex-1 md:flex-none px-8">People</TabsTrigger>
                </TabsList>

                <TabsContent value="assignments" className="space-y-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold">Upcoming Work</h2>
                        <Button size="sm" variant="outline">Sync to Calendar</Button>
                    </div>

                    <div className="space-y-3">
                        {assignments.map((assignment) => (
                            <Card key={assignment.id} className="hover:bg-white/5 transition-all border-white/10 bg-surface/30 group">
                                <CardContent className="p-4">
                                    <div className="flex items-center justify-between gap-4">
                                        <div className="flex items-center gap-4 flex-1 min-w-0">
                                            <div className="text-3xl flex-shrink-0">
                                                {getUrgencyEmoji(assignment.deadline)}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className="text-lg">{getTypeEmoji(assignment.type)}</span>
                                                    <h3 className="font-bold text-lg truncate">{assignment.title}</h3>
                                                    {assignment.type && (
                                                        <span className="px-2 py-0.5 rounded text-xs font-bold bg-primary/20 text-primary">
                                                            {assignment.type}
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-text/60 line-clamp-1">{assignment.description}</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-6 flex-shrink-0">
                                            <div className="text-right">
                                                <div className={`font-bold ${getUrgencyColor(assignment.deadline)}`}>
                                                    {getDaysLeft(assignment.deadline)}
                                                </div>
                                                {assignment.deadline && (
                                                    <div className="text-xs text-text/60">
                                                        {new Date(assignment.deadline).toLocaleDateString('en-US', {
                                                            month: 'short',
                                                            day: 'numeric',
                                                            hour: '2-digit',
                                                            minute: '2-digit'
                                                        })}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="flex gap-2">
                                                <a href={assignment.alternateLink} target="_blank" rel="noopener noreferrer">
                                                    <Button size="sm" variant="secondary">
                                                        <ExternalLink className="w-4 h-4" />
                                                    </Button>
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex flex-col gap-2 min-w-[140px]">
                                        <a href={assignment.alternateLink} target="_blank" rel="noopener noreferrer" className="w-full">
                                            <Button size="sm" variant="secondary" className="w-full justify-start">
                                                <ExternalLink className="w-4 h-4 mr-2" />
                                                Open in New Tab
                                            </Button>
                                        </a>
                                        <Button size="sm" variant="outline" className="w-full justify-start">
                                            <Download className="w-4 h-4 mr-2" />
                                            Save
                                        </Button>
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            className="w-full justify-start"
                                            onClick={() => handleOpenWith(assignment.alternateLink)}
                                        >
                                            <FileText className="w-4 h-4 mr-2" />
                                            Open With...
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="materials">
                    <div className="p-8 text-center text-text/60 bg-surface/30 rounded-xl border border-white/10">
                        No materials found for this course.
                    </div>
                </TabsContent>

                <TabsContent value="grades">
                    {grades ? (
                        <div className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <Card className="bg-surface/30 border-white/10">
                                    <CardContent className="p-6 text-center">
                                        <h3 className="text-sm font-medium text-text/60 mb-1">Current Grade</h3>
                                        <div className="text-4xl font-bold text-primary">{grades.currentGrade.toFixed(1)}%</div>
                                    </CardContent>
                                </Card>
                                <Card className="bg-surface/30 border-white/10">
                                    <CardContent className="p-6 text-center">
                                        <h3 className="text-sm font-medium text-text/60 mb-1">Projected Grade</h3>
                                        <div className="text-4xl font-bold text-secondary">{grades.projectedGrade.toFixed(1)}%</div>
                                    </CardContent>
                                </Card>
                            </div>

                            <Card className="bg-surface/30 border-white/10">
                                <CardContent className="p-6">
                                    <h3 className="text-lg font-bold mb-4">Grade Breakdown</h3>
                                    <div className="space-y-4">
                                        {grades.categories.map((cat) => (
                                            <div key={cat.name} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                                                <div>
                                                    <div className="font-medium">{cat.name}</div>
                                                    <div className="text-xs text-text/60">{cat.items} items • {cat.weight}% weight</div>
                                                </div>
                                                <div className="text-right">
                                                    <div className="font-bold">{cat.percentage.toFixed(1)}%</div>
                                                    <div className="text-xs text-text/60">{cat.score.toFixed(1)} / {cat.max.toFixed(1)} pts</div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    ) : (
                        <div className="p-8 text-center text-text/60 bg-surface/30 rounded-xl border border-white/10">
                            Loading grades...
                        </div>
                    )}
                </TabsContent>

                <TabsContent value="people">
                    <div className="p-8 text-center text-text/60 bg-surface/30 rounded-xl border border-white/10">
                        Teacher info coming soon.
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    )
}
