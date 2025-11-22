package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"classroom-assistant-backend/internal/services"
	"classroom-assistant-backend/internal/models"
)

var calendarService = services.NewCalendarService()

func GetEvents(c *gin.Context) {
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}
	
	events, err := calendarService.GetUpcomingEvents(c.Request.Context(), token, 50)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, events)
}

func CreateEvent(c *gin.Context) {
	var event models.CalendarEvent
	if err := c.ShouldBindJSON(&event); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}
	
	created, err := calendarService.CreateEvent(c.Request.Context(), token, &event)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, created)
}

func UpdateEvent(c *gin.Context) {
	// TODO: Implement update
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Not implemented"})
}

func DeleteEvent(c *gin.Context) {
	id := c.Param("id")
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}

	if err := calendarService.DeleteEvent(c.Request.Context(), token, id); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Event deleted"})
}

func SyncAssignments(c *gin.Context) {
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}
	
	// 1. Get all courses
	courses, err := classroomService.GetCourses(c.Request.Context(), token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch courses: " + err.Error()})
		return
	}

	// 2. Fetch all assignments from all courses
	var allAssignments []*models.Assignment
	for _, course := range courses {
		assignments, err := classroomService.GetAssignments(c.Request.Context(), token, course.ID)
		if err != nil {
			continue // Skip courses with errors
		}
		// Add course name to each assignment
		for _, a := range assignments {
			a.CourseName = course.Name
		}
		allAssignments = append(allAssignments, assignments...)
	}

	// 3. Sync assignments to calendar
	synced, err := calendarService.SyncAssignmentsToCalendar(c.Request.Context(), token, allAssignments)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to sync: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Assignments synced successfully",
		"synced":  synced,
		"total":   len(allAssignments),
	})
}

func CleanupPastEvents(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Not implemented"})
}
