package auth

import (
	"classroom-assistant-backend/internal/database"
	"classroom-assistant-backend/internal/models"
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/oauth2"
	"golang.org/x/oauth2/google"
	"gorm.io/gorm"
)

var (
	googleOauthConfig *oauth2.Config
	jwtSecret         []byte
)

func InitAuth() {
	redirectURL := os.Getenv("GOOGLE_REDIRECT_URL")
	if redirectURL == "" {
		redirectURL = "http://localhost:8080/api/auth/callback"
	}

	googleOauthConfig = &oauth2.Config{
		RedirectURL:  redirectURL,
		ClientID:     os.Getenv("GOOGLE_CLIENT_ID"),
		ClientSecret: os.Getenv("GOOGLE_CLIENT_SECRET"),
		Scopes: []string{
			"https://www.googleapis.com/auth/userinfo.email",
			"https://www.googleapis.com/auth/userinfo.profile",
			// Classroom scopes
			"https://www.googleapis.com/auth/classroom.courses.readonly",
			"https://www.googleapis.com/auth/classroom.coursework.me",
			"https://www.googleapis.com/auth/classroom.coursework.students.readonly",
			"https://www.googleapis.com/auth/classroom.courseworkmaterials.readonly",
			"https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
			"https://www.googleapis.com/auth/classroom.rosters.readonly",
			// Calendar scopes
			"https://www.googleapis.com/auth/calendar",
			"https://www.googleapis.com/auth/calendar.events",
			// Gmail scope
			"https://www.googleapis.com/auth/gmail.send",
		},
		Endpoint: google.Endpoint,
	}

	jwtSecret = []byte(os.Getenv("JWT_SECRET"))
	if len(jwtSecret) == 0 {
		// Fallback for dev if not set (DO NOT USE IN PROD)
		jwtSecret = []byte("dev-secret-key-change-me")
	}
}

func GetLoginURL() string {
	oauthState := generateStateOauthCookie()
	return googleOauthConfig.AuthCodeURL(oauthState)
}

func HandleCallback(code string) (string, *models.User, error) {
	token, err := googleOauthConfig.Exchange(context.Background(), code)
	if err != nil {
		return "", nil, fmt.Errorf("code exchange failed: %s", err.Error())
	}

	userInfo, err := getUserInfo(token.AccessToken)
	if err != nil {
		return "", nil, fmt.Errorf("failed to get user info: %s", err.Error())
	}

	user := models.User{
		GoogleID:     userInfo.ID,
		Email:        userInfo.Email,
		Name:         userInfo.Name,
		Picture:      userInfo.Picture,
		AccessToken:  token.AccessToken,
		RefreshToken: token.RefreshToken,
		TokenExpiry:  token.Expiry,
		LastLogin:    time.Now(),
	}

	// Create or Update User
	var existingUser models.User
	result := database.DB.Where("google_id = ?", user.GoogleID).First(&existingUser)

	if result.Error == gorm.ErrRecordNotFound {
		database.DB.Create(&user)
	} else {
		user.ID = existingUser.ID
		database.DB.Model(&existingUser).Updates(user)
	}

	// Generate JWT
	jwtToken, err := generateJWT(user.ID)
	if err != nil {
		return "", nil, err
	}

	return jwtToken, &user, nil
}

func generateStateOauthCookie() string {
	b := make([]byte, 16)
	rand.Read(b)
	return base64.URLEncoding.EncodeToString(b)
}

type GoogleUserInfo struct {
	ID      string `json:"id"`
	Email   string `json:"email"`
	Name    string `json:"name"`
	Picture string `json:"picture"`
}

func getUserInfo(accessToken string) (*GoogleUserInfo, error) {
	resp, err := http.Get("https://www.googleapis.com/oauth2/v2/userinfo?access_token=" + accessToken)
	if err != nil {
		return nil, fmt.Errorf("failed getting user info: %s", err.Error())
	}
	defer resp.Body.Close()

	content, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed reading response body: %s", err.Error())
	}

	var userInfo GoogleUserInfo
	if err := json.Unmarshal(content, &userInfo); err != nil {
		return nil, fmt.Errorf("failed parsing json: %s", err.Error())
	}

	return &userInfo, nil
}

func generateJWT(userID uint) (string, error) {
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"sub": userID,
		"exp": time.Now().Add(time.Hour * 24 * 7).Unix(), // 7 days
	})

	tokenString, err := token.SignedString(jwtSecret)
	if err != nil {
		return "", err
	}

	return tokenString, nil
}

func ValidateToken(tokenString string) (uint, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
		}
		return jwtSecret, nil
	})

	if err != nil {
		return 0, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		userID := uint(claims["sub"].(float64))
		return userID, nil
	}

	return 0, errors.New("invalid token")
}

func GetClient(ctx context.Context, token *oauth2.Token) *http.Client {
	return googleOauthConfig.Client(ctx, token)
}
