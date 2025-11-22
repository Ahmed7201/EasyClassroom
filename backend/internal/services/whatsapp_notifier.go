package services

import (
	"fmt"
	"net/http"
	"net/url"
	"sort"
	"strings"
	"time"

	"classroom-assistant-backend/internal/models"
)

type WhatsAppNotifier struct{}

func NewWhatsAppNotifier() *WhatsAppNotifier {
	return &WhatsAppNotifier{}
}

func (n *WhatsAppNotifier) SendMessage(phone, apiKey, message string) error {
	baseURL := "https://api.callmebot.com/whatsapp.php"
	params := url.Values{}
	params.Add("phone", phone)
	params.Add("text", message)
	params.Add("apikey", apiKey)

	resp, err := http.Get(fmt.Sprintf("%s?%s", baseURL, params.Encode()))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return fmt.Errorf("failed to send message: status code %d", resp.StatusCode)
	}

	return nil
}

func (n *WhatsAppNotifier) SendDailySummary(phone, apiKey string, assignments []*models.Assignment) error {
	if len(assignments) == 0 {
		return n.SendMessage(phone, apiKey, "✅ No pending assignments! Enjoy your day! 🎉")
	}

	// Filter and sort assignments
	var pending []*models.Assignment
	now := time.Now()

	for _, a := range assignments {
		if a.Deadline != nil && a.Deadline.After(now) {
			pending = append(pending, a)
		}
	}

	if len(pending) == 0 {
		return n.SendMessage(phone, apiKey, "✅ No upcoming assignments! Enjoy your day! 🎉")
	}

	// Sort by deadline
	sort.Slice(pending, func(i, j int) bool {
		return pending[i].Deadline.Before(*pending[j].Deadline)
	})

	var sb strings.Builder
	sb.WriteString("🌅 *Daily Assignment Summary* 📚\n\n")

	for _, a := range pending {
		daysLeft := int(time.Until(*a.Deadline).Hours() / 24)
		
		icon := "🟢"
		if daysLeft < 2 {
			icon = "🔴"
		} else if daysLeft < 5 {
			icon = "🟠"
		}

		sb.WriteString(fmt.Sprintf("%s *%s*\n", icon, a.Title))
		sb.WriteString(fmt.Sprintf("   📘 %s\n", a.CourseName)) // Note: CourseName needs to be populated
		sb.WriteString(fmt.Sprintf("   🕐 Due: %s (%d days)\n\n", a.Deadline.Format("Mon, Jan 02 3:04 PM"), daysLeft))
	}

	sb.WriteString("\n_Sent by Academic Assistant_ 🤖")

	return n.SendMessage(phone, apiKey, sb.String())
}

func (n *WhatsAppNotifier) SendNewAssignmentAlert(phone, apiKey string, assignment *models.Assignment) error {
	var sb strings.Builder
	sb.WriteString("🚨 *New Assignment Alert!* 🚨\n\n")
	sb.WriteString(fmt.Sprintf("📝 *%s*\n", assignment.Title))
	sb.WriteString(fmt.Sprintf("📘 %s\n", assignment.CourseName))
	
	if assignment.Deadline != nil {
		sb.WriteString(fmt.Sprintf("🕐 Due: %s\n", assignment.Deadline.Format("Mon, Jan 02 3:04 PM")))
	}
	
	sb.WriteString(fmt.Sprintf("\n%s", assignment.AlternateLink))

	return n.SendMessage(phone, apiKey, sb.String())
}
