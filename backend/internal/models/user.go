package models

import (
	"time"

	"gorm.io/gorm"
)

type User struct {
	gorm.Model
	GoogleID         string           `json:"id" gorm:"uniqueIndex"`
	Email            string           `json:"email" gorm:"uniqueIndex"`
	Name             string           `json:"name"`
	Picture          string           `json:"picture"`
	Timezone         string           `json:"timezone" gorm:"default:'UTC'"`
	WhatsAppSettings WhatsAppSettings `json:"whatsappSettings" gorm:"embedded"`
	AccessToken      string           `json:"-"` // Stored encrypted in real app
	RefreshToken     string           `json:"-"` // Stored encrypted in real app
	TokenExpiry      time.Time        `json:"-"`
	LastLogin        time.Time        `json:"lastLogin"`
}

type Session struct {
	ID        string    `json:"id" gorm:"primaryKey"`
	UserID    uint      `json:"user_id"`
	User      User      `json:"user"`
	ExpiresAt time.Time `json:"expires_at"`
	CreatedAt time.Time `json:"created_at"`
}

type WhatsAppSettings struct {
	PhoneNumber         string `json:"phoneNumber"`
	APIKey              string `json:"apiKey"`
	DailySummaryEnabled bool   `json:"dailySummaryEnabled"`
	NewAssignmentAlerts bool   `json:"newAssignmentAlerts"`
	SummaryTime         string `json:"summaryTime"`
}
