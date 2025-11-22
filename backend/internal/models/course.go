package models

import "time"

type Course struct {
	ID                 string `json:"id"`
	Name               string `json:"name"`
	Section            string `json:"section,omitempty"`
	DescriptionHeading string `json:"descriptionHeading,omitempty"`
	Description        string `json:"description,omitempty"`
	Room               string `json:"room,omitempty"`
	OwnerID            string `json:"ownerId"`
	CreationTime       string `json:"creationTime"`
	UpdateTime         string `json:"updateTime"`
	EnrollmentCode     string `json:"enrollmentCode,omitempty"`
	CourseState        string `json:"courseState"`
	AlternateLink      string `json:"alternateLink"`
	TeacherGroupEmail  string `json:"teacherGroupEmail,omitempty"`
	CourseGroupEmail   string `json:"courseGroupEmail,omitempty"`
}

type Assignment struct {
	ID            string     `json:"id"`
	CourseID      string     `json:"courseId"`
	CourseName    string     `json:"courseName,omitempty"`
	Title         string     `json:"title"`
	Description   string     `json:"description,omitempty"`
	Materials     []Material `json:"materials,omitempty"`
	State         string     `json:"state"`
	AlternateLink string     `json:"alternateLink"`
	CreationTime  string     `json:"creationTime"`
	UpdateTime    string     `json:"updateTime"`
	DueDate       *DueDate   `json:"dueDate,omitempty"`
	DueTime       *TimeOfDay `json:"dueTime,omitempty"`
	Deadline      *time.Time `json:"deadline,omitempty"` // Calculated field
	MaxPoints     float64    `json:"maxPoints,omitempty"`
	WorkType      string     `json:"workType"`
	Type          string     `json:"type"` // Inferred type (Assignment, Quiz, etc.)
	IsArchived    bool       `json:"isArchived"`
}

type Material struct {
	DriveFile    *DriveFile    `json:"driveFile,omitempty"`
	YouTubeVideo *YouTubeVideo `json:"youtubeVideo,omitempty"`
	Link         *Link         `json:"link,omitempty"`
	Form         *Form         `json:"form,omitempty"`
}

type DriveFile struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	AlternateLink string `json:"alternateLink"`
	ThumbnailURL  string `json:"thumbnailUrl,omitempty"`
}

type YouTubeVideo struct {
	ID            string `json:"id"`
	Title         string `json:"title"`
	AlternateLink string `json:"alternateLink"`
	ThumbnailURL  string `json:"thumbnailUrl,omitempty"`
}

type Link struct {
	URL          string `json:"url"`
	Title        string `json:"title,omitempty"`
	ThumbnailURL string `json:"thumbnailUrl,omitempty"`
}

type Form struct {
	FormURL      string `json:"formUrl"`
	ResponseURL  string `json:"responseUrl"`
	Title        string `json:"title,omitempty"`
	ThumbnailURL string `json:"thumbnailUrl,omitempty"`
}

type DueDate struct {
	Year  int `json:"year"`
	Month int `json:"month"`
	Day   int `json:"day"`
}

type TimeOfDay struct {
	Hours   int `json:"hours"`
	Minutes int `json:"minutes"`
	Seconds int `json:"seconds,omitempty"`
	Nanos   int `json:"nanos,omitempty"`
}

type GradeCategory struct {
	Name   string      `json:"name"`
	Weight float64     `json:"weight"`
	Grades []GradeItem `json:"grades,omitempty"`
}

type GradeItem struct {
	Name     string `json:"name"`
	MaxScore int    `json:"maxScore"`
	Score    int    `json:"score,omitempty"`
	DueDate  string `json:"dueDate,omitempty"`
}
