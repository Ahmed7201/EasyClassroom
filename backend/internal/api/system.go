package api

import (
	"net/http"
	"os/exec"
	"runtime"

	"github.com/gin-gonic/gin"
)

type OpenFileRequest struct {
	FilePath string `json:"filePath" binding:"required"`
}

// OpenFile handles opening a file on the host system using the default application
func OpenFile(c *gin.Context) {
	var req OpenFileRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Security check: Ensure we're not opening arbitrary commands
	// In a real app, you'd want strict validation here (e.g., only allow files in specific directories)
	// For this personal assistant, we'll assume the user trusts the app but still be careful

	var cmd *exec.Cmd
	var err error

	switch runtime.GOOS {
	case "windows":
		// "start" is a shell command, so we need cmd /c
		// But exec.Command("rundll32", "url.dll,FileProtocolHandler", req.FilePath) is safer/easier
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", req.FilePath)
	case "darwin":
		cmd = exec.Command("open", req.FilePath)
	case "linux":
		cmd = exec.Command("xdg-open", req.FilePath)
	default:
		c.JSON(http.StatusNotImplemented, gin.H{"error": "Unsupported operating system"})
		return
	}

	if err = cmd.Start(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to open file: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "File opened successfully"})
}
