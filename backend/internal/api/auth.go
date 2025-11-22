package api

import (
	"classroom-assistant-backend/internal/auth"
	"classroom-assistant-backend/internal/database"
	"classroom-assistant-backend/internal/models"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
)

func HandleLogin(c *gin.Context) {
	url := auth.GetLoginURL()
	c.Redirect(http.StatusTemporaryRedirect, url)
}

func HandleCallback(c *gin.Context) {
	code := c.Query("code")
	if code == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Code not found"})
		return
	}

	token, user, err := auth.HandleCallback(code)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Redirect to frontend with token
	frontendURL := os.Getenv("FRONTEND_URL")
	if frontendURL == "" {
		frontendURL = "http://localhost:5173"
	}
	
	// In a real app, we might want to set a cookie or send this via a postMessage if it's a popup
	// For now, passing it as a query param is a simple way to get started
	c.Redirect(http.StatusTemporaryRedirect, frontendURL+"/login?token="+token+"&user_id="+user.GoogleID)
}

func HandleRefresh(c *gin.Context) {
	// TODO: Implement refresh logic using stored refresh token
	c.JSON(http.StatusNotImplemented, gin.H{"error": "Not implemented"})
}

func HandleLogout(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"message": "Logged out"})
}

func HandleProfile(c *gin.Context) {
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

	c.JSON(http.StatusOK, gin.H{
		"id":      user.GoogleID,
		"email":   user.Email,
		"name":    user.Name,
		"picture": user.Picture,
	})
}
