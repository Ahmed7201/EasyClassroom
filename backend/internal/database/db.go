package database

import (
	"classroom-assistant-backend/internal/models"
	"database/sql"
	"log"
	"os"
	"path/filepath"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
	_ "modernc.org/sqlite" // Pure Go SQLite driver
)

var DB *gorm.DB

func InitDB() {
	var err error
	dbPath := os.Getenv("DATABASE_PATH")
	if dbPath == "" {
		dbPath = "classroom.db"
	}

	// Ensure directory exists if path contains directories
	dir := filepath.Dir(dbPath)
	if dir != "." {
		if err := os.MkdirAll(dir, 0755); err != nil {
			log.Fatal("Failed to create database directory:", err)
		}
	}

	// Open with modernc.org/sqlite (pure Go, no CGO)
	sqlDB, err := sql.Open("sqlite", dbPath)
	if err != nil {
		log.Fatal("Failed to open database:", err)
	}

	DB, err = gorm.Open(sqlite.Dialector{Conn: sqlDB}, &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Auto Migrate the schema
	err = DB.AutoMigrate(&models.User{}, &models.Session{}, &models.AssignmentState{})
	if err != nil {
		log.Fatal("Failed to migrate database schema:", err)
	}

	log.Println("Database connected and migrated successfully")
}
