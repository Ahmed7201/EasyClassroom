package api

import (
	"net/http"

	"classroom-assistant-backend/internal/database"
	"classroom-assistant-backend/internal/models"
	"classroom-assistant-backend/internal/services"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

var classroomService = services.NewClassroomService()

func GetCourses(c *gin.Context) {
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}

	courses, err := classroomService.GetCourses(c.Request.Context(), token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, courses)
}

func GetCourse(c *gin.Context) {
	id := c.Param("id")
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}

	course, err := classroomService.GetCourse(c.Request.Context(), token, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, course)
}

func GetAssignments(c *gin.Context) {
	id := c.Param("id")
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}

	assignments, err := classroomService.GetAssignments(c.Request.Context(), token, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Fetch local state for these assignments
	userID, _ := c.Get("userID")
	var states []models.AssignmentState
	if err := database.DB.Where("user_id = ?", userID).Find(&states).Error; err != nil {
		// Log error but continue without state
		// log.Println("Failed to fetch assignment states:", err)
	}

	// Create a map for faster lookup
	stateMap := make(map[string]bool)
	for _, state := range states {
		stateMap[state.AssignmentID] = state.IsArchived
	}

	// Merge state
	for i := range assignments {
		if isArchived, exists := stateMap[assignments[i].ID]; exists {
			assignments[i].IsArchived = isArchived
		}
	}

	c.JSON(http.StatusOK, assignments)
}

type ToggleStateRequest struct {
	IsArchived bool `json:"isArchived"`
}

func ToggleAssignmentState(c *gin.Context) {
	id := c.Param("id")
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req ToggleStateRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	var state models.AssignmentState
	err := database.DB.Where("assignment_id = ? AND user_id = ?", id, userID).First(&state).Error

	if err != nil {
		if err == gorm.ErrRecordNotFound {
			// Create new record
			state = models.AssignmentState{
				AssignmentID: id,
				UserID:       userID.(uint),
				IsArchived:   req.IsArchived,
			}
			if err := database.DB.Create(&state).Error; err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save state"})
				return
			}
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Database error"})
			return
		}
	} else {
		// Update existing record
		state.IsArchived = req.IsArchived
		if err := database.DB.Save(&state).Error; err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update state"})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "State updated", "isArchived": state.IsArchived})
}

func GetMaterials(c *gin.Context) {
	// Materials are part of assignments/coursework in API
	// This endpoint might filter them specifically
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Not implemented"})
}

func GetCourseGrades(c *gin.Context) {
	id := c.Param("id")
	token, err := getUserToken(c)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Failed to get user token"})
		return
	}

	// 1. Get Course Details (for name)
	course, err := classroomService.GetCourse(c.Request.Context(), token, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch course: " + err.Error()})
		return
	}

	// 2. Get Assignments
	assignments, err := classroomService.GetAssignments(c.Request.Context(), token, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch assignments: " + err.Error()})
		return
	}

	// 3. Calculate Grades
	engine := services.NewGradingEngine()
	grades := engine.CalculateGrades(course.Name, assignments)

	c.JSON(http.StatusOK, grades)
}

func GetTeachers(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Not implemented"})
}
