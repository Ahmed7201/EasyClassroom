// User types
export interface User {
    id: string
    email: string
    name: string
    picture?: string
}

// Course types
export interface Course {
    id: string
    name: string
    section?: string
    descriptionHeading?: string
    description?: string
    room?: string
    ownerId: string
    creationTime: string
    updateTime: string
    enrollmentCode?: string
    courseState: 'ACTIVE' | 'ARCHIVED' | 'PROVISIONED' | 'DECLINED' | 'SUSPENDED'
    alternateLink: string
    teacherGroupEmail?: string
    courseGroupEmail?: string
    guardiansEnabled?: boolean
    calendarId?: string
}

// Assignment types
export interface Assignment {
    id: string
    courseId: string
    courseName?: string
    title: string
    description?: string
    materials?: Material[]
    state: 'PUBLISHED' | 'DRAFT' | 'DELETED'
    alternateLink: string
    creationTime: string
    updateTime: string
    dueDate?: DueDate
    dueTime?: TimeOfDay
    deadline?: string // ISO format
    scheduledTime?: string
    maxPoints?: number
    workType: 'ASSIGNMENT' | 'SHORT_ANSWER_QUESTION' | 'MULTIPLE_CHOICE_QUESTION'
    submissionModificationMode?: string
    assigneeMode: 'ALL_STUDENTS' | 'INDIVIDUAL_STUDENTS'
    type?: 'ASSIGNMENT' | 'QUIZ' | 'EXAM' | 'LAB' | 'PROJECT' | 'MIDTERM' | 'FINAL'
    isArchived?: boolean
}

export interface DueDate {
    year: number
    month: number
    day: number
}

export interface TimeOfDay {
    hours: number
    minutes: number
    seconds?: number
    nanos?: number
}

export interface Material {
    driveFile?: DriveFile
    youtubeVideo?: YouTubeVideo
    link?: Link
    form?: Form
}

export interface DriveFile {
    id: string
    title: string
    alternateLink: string
    thumbnailUrl?: string
}

export interface YouTubeVideo {
    id: string
    title: string
    alternateLink: string
    thumbnailUrl?: string
}

export interface Link {
    url: string
    title?: string
    thumbnailUrl?: string
}

export interface Form {
    formUrl: string
    responseUrl: string
    title: string
    thumbnailUrl?: string
}

// Calendar event types
export interface CalendarEvent {
    id: string
    summary: string
    description?: string
    location?: string
    start: EventDateTime
    end: EventDateTime
    attendees?: Attendee[]
    creator?: Person
    organizer?: Person
    htmlLink?: string
    colorId?: string
    status: 'confirmed' | 'tentative' | 'cancelled'
}

export interface EventDateTime {
    dateTime?: string // ISO format
    timeZone?: string
    date?: string // For all-day events
}

export interface Attendee {
    email: string
    displayName?: string
    responseStatus?: 'needsAction' | 'declined' | 'tentative' | 'accepted'
}

export interface Person {
    email: string
    displayName?: string
    self?: boolean
}

// Teacher types
export interface Teacher {
    courseId: string
    userId: string
    profile: UserProfile
}

export interface UserProfile {
    id: string
    name: NameInfo
    emailAddress: string
    photoUrl?: string
}

export interface NameInfo {
    givenName: string
    familyName: string
    fullName: string
}

// Grade types
export interface GradeCategory {
    name: string
    weight: number
    grades: GradeItem[]
}

export interface GradeItem {
    name: string
    score?: number
    maxScore: number
    weight?: number
    dueDate?: string
}

export interface GradeReport {
    categories: GradeCategoryResult[]
    currentGrade: number
    projectedGrade: number
}

export interface GradeCategoryResult {
    name: string
    weight: number
    score: number
    max: number
    percentage: number
    items: number
}

// WhatsApp notification types
export interface WhatsAppSettings {
    phoneNumber: string
    apiKey: string
    dailySummaryEnabled: boolean
    newAssignmentAlerts: boolean
    summaryTime: string
}

// API Response types
export interface APIResponse<T> {
    data: T
    message?: string
    error?: string
}

export interface PaginatedResponse<T> {
    data: T[]
    nextPageToken?: string
    totalCount?: number
}
