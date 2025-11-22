package services

import (
	"context"
	"fmt"
	"time"

	"classroom-assistant-backend/internal/auth"
	"classroom-assistant-backend/internal/models"
	"golang.org/x/oauth2"
	"google.golang.org/api/calendar/v3"
	"google.golang.org/api/option"
)

type CalendarService struct{}

func NewCalendarService() *CalendarService {
	return &CalendarService{}
}

func (s *CalendarService) getClient(ctx context.Context, token *oauth2.Token) (*calendar.Service, error) {
	client := auth.GetClient(ctx, token)
	return calendar.NewService(ctx, option.WithHTTPClient(client))
}

func (s *CalendarService) GetUpcomingEvents(ctx context.Context, token *oauth2.Token, maxResults int64) ([]*models.CalendarEvent, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	t := time.Now().Format(time.RFC3339)
	events, err := srv.Events.List("primary").ShowDeleted(false).
		SingleEvents(true).TimeMin(t).MaxResults(maxResults).OrderBy("startTime").Do()
	if err != nil {
		return nil, err
	}

	var calendarEvents []*models.CalendarEvent
	for _, item := range events.Items {
		calendarEvents = append(calendarEvents, &models.CalendarEvent{
			ID:          item.Id,
			Summary:     item.Summary,
			Description: item.Description,
			Location:    item.Location,
			Start: models.EventDateTime{
				DateTime: item.Start.DateTime,
				Date:     item.Start.Date,
				TimeZone: item.Start.TimeZone,
			},
			End: models.EventDateTime{
				DateTime: item.End.DateTime,
				Date:     item.End.Date,
				TimeZone: item.End.TimeZone,
			},
			HtmlLink: item.HtmlLink,
			Status:   item.Status,
		})
	}

	return calendarEvents, nil
}

func (s *CalendarService) CreateEvent(ctx context.Context, token *oauth2.Token, event *models.CalendarEvent) (*models.CalendarEvent, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	googleEvent := &calendar.Event{
		Summary:     event.Summary,
		Location:    event.Location,
		Description: event.Description,
		Start: &calendar.EventDateTime{
			DateTime: event.Start.DateTime,
			TimeZone: event.Start.TimeZone,
		},
		End: &calendar.EventDateTime{
			DateTime: event.End.DateTime,
			TimeZone: event.End.TimeZone,
		},
	}

	createdEvent, err := srv.Events.Insert("primary", googleEvent).Do()
	if err != nil {
		return nil, err
	}

	event.ID = createdEvent.Id
	event.HtmlLink = createdEvent.HtmlLink
	return event, nil
}

func (s *CalendarService) DeleteEvent(ctx context.Context, token *oauth2.Token, eventID string) error {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return err
	}

	return srv.Events.Delete("primary", eventID).Do()
}

// SyncAssignmentsToCalendar creates calendar events for assignments with deadlines
func (s *CalendarService) SyncAssignmentsToCalendar(ctx context.Context, token *oauth2.Token, assignments []*models.Assignment) (int, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return 0, err
	}

	// Get existing events to prevent duplicates
	t := time.Now().Format(time.RFC3339)
	events, err := srv.Events.List("primary").ShowDeleted(false).
		SingleEvents(true).TimeMin(t).Do()
	if err != nil {
		return 0, err
	}

	existingTitles := make(map[string]bool)
	for _, item := range events.Items {
		existingTitles[item.Summary] = true
	}

	count := 0
	for _, assignment := range assignments {
		if assignment.Deadline == nil {
			continue
		}

		// Format title: [CourseName] Title
		title := fmt.Sprintf("[%s] %s", assignment.CourseName, assignment.Title)
		
		if existingTitles[title] {
			continue
		}

		// Event starts 6 hours before deadline and ends at deadline
		start := assignment.Deadline.Add(-6 * time.Hour)
		end := *assignment.Deadline

		event := &calendar.Event{
			Summary:     title,
			Description: fmt.Sprintf("Course: %s\n%s\n\nLink: %s", assignment.CourseName, assignment.Description, assignment.AlternateLink),
			Start: &calendar.EventDateTime{
				DateTime: start.Format(time.RFC3339),
				TimeZone: "UTC", // Deadlines are stored in UTC
			},
			End: &calendar.EventDateTime{
				DateTime: end.Format(time.RFC3339),
				TimeZone: "UTC",
			},
			Reminders: &calendar.EventReminders{
				UseDefault: false,
				Overrides: []*calendar.EventReminder{
					{
						Method:  "popup",
						Minutes: 360, // 6 hours before
					},
				},
			},
		}

		_, err := srv.Events.Insert("primary", event).Do()
		if err != nil {
			// Log error but continue with other assignments
			fmt.Printf("Failed to sync assignment %s: %v\n", assignment.Title, err)
			continue
		}
		count++
	}

	return count, nil
}
