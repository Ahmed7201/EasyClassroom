package api

import (
	"classroom-assistant-backend/internal/database"
	"classroom-assistant-backend/internal/models"
	"golang.org/x/oauth2"
	"github.com/gin-gonic/gin"
)

// getUserToken retrieves the user's OAuth token from the database
func getUserToken(c *gin.Context) (*oauth2.Token, error) {
	userID, exists := c.Get("userID")
	if !exists {
		return nil, nil
	}

	var user models.User
	if err := database.DB.First(&user, userID).Error; err != nil {
		return nil, err
	}

	return &oauth2.Token{
		AccessToken:  user.AccessToken,
		RefreshToken: user.RefreshToken,
		Expiry:       user.TokenExpiry,
	}, nil
}
