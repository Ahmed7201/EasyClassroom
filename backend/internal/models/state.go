package models

import "gorm.io/gorm"

type AssignmentState struct {
	gorm.Model
	AssignmentID string `json:"assignmentId" gorm:"uniqueIndex:idx_user_assignment"`
	UserID       uint   `json:"userId" gorm:"uniqueIndex:idx_user_assignment"`
	IsArchived   bool   `json:"isArchived" gorm:"default:false"`
}
