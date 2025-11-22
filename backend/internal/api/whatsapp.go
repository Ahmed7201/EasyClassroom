package api

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"golang.org/x/oauth2"
	"classroom-assistant-backend/internal/services"
	"classroom-assistant-backend/internal/models"
)

var whatsappNotifier = services.NewWhatsAppNotifier()

func ConfigureWhatsApp(c *gin.Context) {
	var settings models.WhatsAppSettings
	if err := c.ShouldBindJSON(&settings); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// TODO: Save settings to DB for authenticated user
	c.JSON(http.StatusOK, gin.H{"message": "Settings saved"})
}

func TestWhatsApp(c *gin.Context) {
	var req struct {
		Phone  string `json:"phone"`
		APIKey string `json:"apiKey"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	err := whatsappNotifier.SendMessage(req.Phone, req.APIKey, "🤖 This is a test message from Academic Assistant!")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Test message sent"})
}

func SendSummary(c *gin.Context) {
	token := &oauth2.Token{AccessToken: "placeholder"}
	
	// 1. Get WhatsApp settings (for now, from request body)
	var settings models.WhatsAppSettings
	if err := c.ShouldBindJSON(&settings); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 2. Get all courses
	courses, err := classroomService.GetCourses(c.Request.Context(), token)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch courses: " + err.Error()})
		return
	}

	// 3. Fetch all assignments from all courses
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

	// 4. Send daily summary
	err = whatsappNotifier.SendDailySummary(settings.PhoneNumber, settings.APIKey, allAssignments)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to send summary: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message": "Daily summary sent successfully",
		"assignments": len(allAssignments),
	})
}

func GetWhatsAppSettings(c *gin.Context) {
	// TODO: Fetch from DB
	c.JSON(http.StatusOK, models.WhatsAppSettings{
		PhoneNumber: "",
		APIKey: "",
		DailySummaryEnabled: false,
		NewAssignmentAlerts: false,
		SummaryTime: "08:00",
	})
}
