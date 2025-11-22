package models

type CalendarEvent struct {
	ID          string        `json:"id"`
	Summary     string        `json:"summary"`
	Description string        `json:"description,omitempty"`
	Location    string        `json:"location,omitempty"`
	Start       EventDateTime `json:"start"`
	End         EventDateTime `json:"end"`
	HtmlLink    string        `json:"htmlLink,omitempty"`
	Status      string        `json:"status,omitempty"`
}

type EventDateTime struct {
	DateTime string `json:"dateTime,omitempty"` // RFC3339
	Date     string `json:"date,omitempty"`     // YYYY-MM-DD
	TimeZone string `json:"timeZone,omitempty"`
}
