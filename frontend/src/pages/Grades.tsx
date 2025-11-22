import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card'
import { coursesApi } from '../api/courses'
import { Course, GradeReport } from '../types/models'

interface CourseGrade {
    course: Course
    report: GradeReport
}

export default function Grades() {
    const [grades, setGrades] = useState<CourseGrade[]>([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const courses = await coursesApi.list()
                const gradesData = await Promise.all(
                    courses.map(async (course) => {
                        try {
                            const report = await coursesApi.getGrades(course.id)
                            return { course, report }
                        } catch (error) {
                            console.error(`Failed to fetch grades for ${course.name}`, error)
                            return null
                        }
                    })
                )
                setGrades(gradesData.filter((g): g is CourseGrade => g !== null))
            } catch (error) {
                console.error('Failed to fetch grades data:', error)
            } finally {
                setIsLoading(false)
            }
        }

        fetchData()
    }, [])

    const getGradeColor = (score: number) => {
        if (score >= 90) return 'text-green-400'
        if (score >= 80) return 'text-blue-400'
        if (score >= 70) return 'text-yellow-400'
        if (score >= 60) return 'text-orange-400'
        return 'text-red-400'
    }

    const getTrendIcon = (current: number, projected: number) => {
        if (projected > current) return <TrendingUp className="w-4 h-4 text-green-400" />
        if (projected < current) return <TrendingDown className="w-4 h-4 text-red-400" />
        return <Minus className="w-4 h-4 text-text/40" />
    }

    if (isLoading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-48 rounded-xl bg-white/5 animate-pulse" />
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-8">📊 Academic Performance</h1>

            <div className="grid gap-6">
                {grades.map(({ course, report }) => (
                    <Card key={course.id} className="bg-surface/30 border-white/10 overflow-hidden">
                        <CardHeader className="bg-white/5 border-b border-white/5 pb-4">
                            <div className="flex justify-between items-start">
                                <div>
                                    <Link to={`/course/${course.id}`} className="hover:underline">
                                        <CardTitle className="text-xl mb-1">{course.name}</CardTitle>
                                    </Link>
                                    <p className="text-sm text-text/60">{course.section}</p>
                                </div>
                                <div className="text-right">
                                    <div className={`text-3xl font-bold ${getGradeColor(report.currentGrade)}`}>
                                        {report.currentGrade.toFixed(1)}%
                                    </div>
                                    <div className="flex items-center justify-end gap-1 text-sm text-text/60">
                                        <span>Projected: {report.projectedGrade.toFixed(1)}%</span>
                                        {getTrendIcon(report.currentGrade, report.projectedGrade)}
                                    </div>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                {report.categories.map((cat) => (
                                    <div key={cat.name} className="bg-black/20 rounded-lg p-3">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-medium text-sm truncate" title={cat.name}>{cat.name}</span>
                                            <span className="text-xs text-text/40">{cat.weight}%</span>
                                        </div>
                                        <div className="flex items-end justify-between">
                                            <div className="text-2xl font-bold">{cat.percentage.toFixed(0)}%</div>
                                            <div className="text-xs text-text/60 mb-1">
                                                {cat.score.toFixed(1)}/{cat.max.toFixed(1)}
                                            </div>
                                        </div>
                                        <div className="mt-2 h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${getGradeColor(cat.percentage)} bg-current opacity-80`}
                                                style={{ width: `${Math.min(cat.percentage, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {grades.length === 0 && (
                    <div className="text-center py-12 text-text/60">
                        No grades available. Check back later!
                    </div>
                )}
            </div>
        </div>
    )
}

