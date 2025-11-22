package main

import (
	"classroom-assistant-backend/internal/api"
	"classroom-assistant-backend/internal/auth"
	"classroom-assistant-backend/internal/database"
	"log"
	"os"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Load environment variables
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found, using system environment variables")
	}

	// Initialize Database
	database.InitDB()

	// Initialize Auth Service
	auth.InitAuth()

	// Set Gin mode
	if os.Getenv("ENV") == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Initialize router
	router := gin.Default()

	// CORS middleware
	config := cors.DefaultConfig()
	config.AllowOrigins = []string{"http://localhost:5173"} // Vite default port
	config.AllowCredentials = true
	config.AllowHeaders = []string{"Origin", "Content-Type", "Accept", "Authorization"}
	router.Use(cors.New(config))

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "healthy",
			"message": "Academic Assistant API v1.0",
		})
	})

	// API routes
	apiGroup := router.Group("/api")
	{
		// Auth routes
		authGroup := apiGroup.Group("/auth")
		{
			authGroup.GET("/login", api.HandleLogin)
			authGroup.GET("/callback", api.HandleCallback)
			authGroup.POST("/refresh", api.HandleRefresh)
			authGroup.POST("/logout", api.HandleLogout)
			authGroup.GET("/profile", auth.AuthMiddleware(), api.HandleProfile)
		}

		// Classroom routes
		classroom := apiGroup.Group("/courses")
		classroom.Use(auth.AuthMiddleware())
		{
			classroom.GET("", api.GetCourses)
			classroom.GET("/:id", api.GetCourse)
			classroom.GET("/:id/assignments", api.GetAssignments)
			classroom.GET("/:id/materials", api.GetMaterials)
			classroom.GET("/:id/grades", api.GetCourseGrades)
			classroom.GET("/:id/teachers", api.GetTeachers)
		}

		// Assignment routes (new)
		assignments := apiGroup.Group("/assignments")
		assignments.Use(auth.AuthMiddleware())
		{
			assignments.PATCH("/:id/state", api.ToggleAssignmentState)
		}

		// Calendar routes
		calendar := apiGroup.Group("/calendar")
		calendar.Use(auth.AuthMiddleware())
		{
			calendar.GET("/events", api.GetEvents)
			calendar.POST("/events", api.CreateEvent)
			calendar.PUT("/events/:id", api.UpdateEvent)
			calendar.DELETE("/events/:id", api.DeleteEvent)
			calendar.POST("/sync", api.SyncAssignments)
			calendar.DELETE("/cleanup", api.CleanupPastEvents)
		}

		// WhatsApp routes
		whatsapp := apiGroup.Group("/whatsapp")
		whatsapp.Use(auth.AuthMiddleware())
		{
			whatsapp.POST("/configure", api.ConfigureWhatsApp)
			whatsapp.POST("/test", api.TestWhatsApp)
			whatsapp.POST("/send-summary", api.SendSummary)
			whatsapp.GET("/settings", api.GetWhatsAppSettings)
		}

		// Settings routes
		settings := apiGroup.Group("/settings")
		settings.Use(auth.AuthMiddleware())
		{
			settings.GET("", api.GetSettings)
			settings.PUT("", api.UpdateSettings)
			settings.GET("/verify-timezone", api.VerifyTimezone)
		}

		// Gmail routes
		gmail := apiGroup.Group("/gmail")
		gmail.Use(auth.AuthMiddleware())
		{
			gmail.POST("/send", api.SendEmail)
		}

		// System routes
		system := apiGroup.Group("/system")
		system.Use(auth.AuthMiddleware())
		{
			system.POST("/open", api.OpenFile)
		}
	}

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}
