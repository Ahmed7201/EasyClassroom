package services

import (
	"context"
	"encoding/base64"
	"fmt"

	"classroom-assistant-backend/internal/auth"
	"golang.org/x/oauth2"
	"google.golang.org/api/gmail/v1"
	"google.golang.org/api/option"
)

type GmailService struct{}

func NewGmailService() *GmailService {
	return &GmailService{}
}

func (s *GmailService) getClient(ctx context.Context, token *oauth2.Token) (*gmail.Service, error) {
	client := auth.GetClient(ctx, token)
	return gmail.NewService(ctx, option.WithHTTPClient(client))
}

// SendEmail sends an email using the user's Gmail account
func (s *GmailService) SendEmail(ctx context.Context, token *oauth2.Token, to, subject, body string) error {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return err
	}

	var message gmail.Message

	// RFC 2822 formatted email
	emailContent := fmt.Sprintf("To: %s\r\n"+
		"Subject: %s\r\n"+
		"Content-Type: text/html; charset=\"UTF-8\"\r\n"+
		"\r\n"+
		"%s", to, subject, body)

	message.Raw = base64.URLEncoding.EncodeToString([]byte(emailContent))

	_, err = srv.Users.Messages.Send("me", &message).Do()
	if err != nil {
		return fmt.Errorf("failed to send email: %v", err)
	}

	return nil
}

// ListEmails fetches recent emails (e.g., from TAs)
// This is a basic implementation; filters can be added
func (s *GmailService) ListEmails(ctx context.Context, token *oauth2.Token, query string, maxResults int64) ([]*gmail.Message, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	resp, err := srv.Users.Messages.List("me").Q(query).MaxResults(maxResults).Do()
	if err != nil {
		return nil, err
	}

	return resp.Messages, nil
}
