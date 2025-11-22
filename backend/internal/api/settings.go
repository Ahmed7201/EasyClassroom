package api

import (
	"classroom-assistant-backend/internal/database"
	"classroom-assistant-backend/internal/models"
	"classroom-assistant-backend/internal/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

type UpdateSettingsRequest struct {
	Timezone            string `json:"timezone"`
	PhoneNumber         string `json:"phoneNumber"`
	APIKey              string `json:"apiKey"`
	DailySummaryEnabled bool   `json:"dailySummaryEnabled"`
	NewAssignmentAlerts bool   `json:"newAssignmentAlerts"`
	SummaryTime         string `json:"summaryTime"`
}

func UpdateSettings(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var req UpdateSettingsRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request body"})
		return
	}

	// Validate timezone if provided
	if req.Timezone != "" {
		tzService := services.NewTimezoneService()
		if !tzService.ValidateTimezone(req.Timezone) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid timezone format. Use IANA format (e.g., 'Africa/Cairo')"})
			return
		}
	}

	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	// Update user settings
	if req.Timezone != "" {
		user.Timezone = req.Timezone
	}
	user.WhatsAppSettings.PhoneNumber = req.PhoneNumber
	user.WhatsAppSettings.APIKey = req.APIKey
	user.WhatsAppSettings.DailySummaryEnabled = req.DailySummaryEnabled
	user.WhatsAppSettings.NewAssignmentAlerts = req.NewAssignmentAlerts
	user.WhatsAppSettings.SummaryTime = req.SummaryTime

	if err := database.DB.Save(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update settings"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"message":          "Settings updated successfully",
		"timezone":         user.Timezone,
		"whatsappSettings": user.WhatsAppSettings,
	})
}

func GetSettings(c *gin.Context) {
	userID, exists := c.Get("userID")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
		return
	}

	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, user.WhatsAppSettings)
}

func VerifyTimezone(c *gin.Context) {
	tz := c.Query("timezone")
	if tz == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Timezone query parameter required"})
		return
	}

	tzService := services.NewTimezoneService()
	if !tzService.ValidateTimezone(tz) {
		c.JSON(http.StatusBadRequest, gin.H{"valid": false, "error": "Invalid IANA timezone"})
		return
	}

	externalTime, err := tzService.VerifyWithExternalAPI(tz)
	if err != nil {
		c.JSON(http.StatusOK, gin.H{
			"valid":             true,
			"verified_external": false,
			"error":             err.Error(),
		})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"valid":             true,
		"verified_external": true,
		"current_time":      externalTime,
	})
}
