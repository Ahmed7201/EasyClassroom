import { useState, useEffect } from 'react'
import {
    format,
    startOfMonth,
    endOfMonth,
    startOfWeek,
    endOfWeek,
    eachDayOfInterval,
    isSameMonth,
    isSameDay,
    addMonths,
    subMonths
} from 'date-fns'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { calendarApi } from '../api/calendar'

export default function Calendar() {
    const [currentDate, setCurrentDate] = useState(new Date())
    const [selectedDate, setSelectedDate] = useState<Date | null>(null)
    const [events, setEvents] = useState<any[]>([])

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const data = await calendarApi.listEvents()
                // Transform API events to local format
                const formattedEvents = data.map((e: any) => ({
                    id: e.id,
                    title: e.summary,
                    start: new Date(e.start.dateTime || e.start.date),
                    end: new Date(e.end.dateTime || e.end.date),
                    type: 'ASSIGNMENT' // Default or derive from event data
                }))
                setEvents(formattedEvents)
            } catch (error) {
                console.error('Failed to fetch events:', error)
            }
        }

        fetchEvents()
    }, [currentDate])

    const monthStart = startOfMonth(currentDate)
    const monthEnd = endOfMonth(monthStart)
    const startDate = startOfWeek(monthStart)
    const endDate = endOfWeek(monthEnd)

    const calendarDays = eachDayOfInterval({
        start: startDate,
        end: endDate
    })

    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    const nextMonth = () => setCurrentDate(addMonths(currentDate, 1))
    const prevMonth = () => setCurrentDate(subMonths(currentDate, 1))
    const goToToday = () => setCurrentDate(new Date())

    const getEventsForDay = (date: Date) => {
        return events.filter(event => isSameDay(event.start, date))
    }

    return (
        <div className="container mx-auto px-4 py-8 h-[calc(100vh-4rem)] flex flex-col">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold">Calendar</h1>
                <div className="flex items-center gap-4">
                    <Button variant="outline" onClick={goToToday}>Today</Button>
                    <div className="flex items-center gap-2">
                        <Button variant="ghost" size="icon" onClick={prevMonth}>←</Button>
                        <span className="text-lg font-medium w-40 text-center">
                            {format(currentDate, 'MMMM yyyy')}
                        </span>
                        <Button variant="ghost" size="icon" onClick={nextMonth}>→</Button>
                    </div>
                    <Button>Sync All</Button>
                </div>
            </div>

            <Card className="flex-1 flex flex-col overflow-hidden bg-surface/30 border-white/10">
                {/* Weekday Headers */}
                <div className="grid grid-cols-7 border-b border-white/10">
                    {weekDays.map(day => (
                        <div key={day} className="py-3 text-center text-sm font-medium text-text/60">
                            {day}
                        </div>
                    ))}
                </div>

                {/* Calendar Grid */}
                <div className="flex-1 grid grid-cols-7 grid-rows-5">
                    {calendarDays.map((day, dayIdx) => {
                        const dayEvents = getEventsForDay(day)
                        const isSelected = selectedDate && isSameDay(day, selectedDate)
                        const isCurrentMonth = isSameMonth(day, monthStart)
                        const isToday = isSameDay(day, new Date())

                        return (
                            <div
                                key={day.toString()}
                                onClick={() => setSelectedDate(day)}
                                className={`
                                    min-h-[100px] border-b border-r border-white/5 p-2 cursor-pointer transition-colors
                                    ${!isCurrentMonth ? 'bg-black/20 text-text/30' : 'hover:bg-white/5'}
                                    ${isSelected ? 'bg-primary/10' : ''}
                                    ${dayIdx % 7 === 0 ? 'border-l' : ''} 
                                `}
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className={`
                                        text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full
                                        ${isToday ? 'bg-primary text-white' : ''}
                                    `}>
                                        {format(day, 'd')}
                                    </span>
                                </div>

                                <div className="space-y-1">
                                    {dayEvents.map(event => (
                                        <div
                                            key={event.id}
                                            className={`
                                                text-xs px-2 py-1 rounded truncate
                                                ${event.type === 'PROJECT' ? 'bg-purple-500/20 text-purple-300' : 'bg-blue-500/20 text-blue-300'}
                                            `}
                                        >
                                            {event.title}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    })}
                </div>
            </Card>
        </div>
    )
}
