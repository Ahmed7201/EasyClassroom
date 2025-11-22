package services

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type TimezoneService struct{}

func NewTimezoneService() *TimezoneService {
	return &TimezoneService{}
}

// ValidateTimezone checks if the provided timezone string is a valid IANA timezone
func (s *TimezoneService) ValidateTimezone(tz string) bool {
	_, err := time.LoadLocation(tz)
	return err == nil
}

// GetLocation returns the time.Location for a given timezone string
func (s *TimezoneService) GetLocation(tz string) (*time.Location, error) {
	if tz == "" {
		return time.UTC, nil
	}
	return time.LoadLocation(tz)
}

// ExternalTimeResponse matches the response from WorldTimeAPI
type ExternalTimeResponse struct {
	Datetime string `json:"datetime"`
	Timezone string `json:"timezone"`
	UtcOffset string `json:"utc_offset"`
}

// VerifyWithExternalAPI checks the current time for a region against WorldTimeAPI
// This is useful to verify if the server's timezone data is up to date or if the user's selection matches reality
func (s *TimezoneService) VerifyWithExternalAPI(tz string) (*time.Time, error) {
	// Use a public API to get the current time for the region
	// Note: In production, you might want to cache this or use a more robust service
	resp, err := http.Get(fmt.Sprintf("http://worldtimeapi.org/api/timezone/%s", tz))
	if err != nil {
		return nil, fmt.Errorf("failed to contact external time API: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("external API returned status: %d", resp.StatusCode)
	}

	var result ExternalTimeResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("failed to decode external API response: %v", err)
	}

	// Parse the datetime from the API (ISO 8601)
	parsedTime, err := time.Parse(time.RFC3339, result.Datetime)
	if err != nil {
		// Try parsing without the offset if RFC3339 fails (some APIs vary)
		// But WorldTimeAPI usually returns ISO 8601 which is compatible with RFC3339
		return nil, fmt.Errorf("failed to parse external time: %v", err)
	}

	return &parsedTime, nil
}

// ConvertToUserTime converts a UTC time to the user's local time
func (s *TimezoneService) ConvertToUserTime(t time.Time, tz string) (time.Time, error) {
	loc, err := s.GetLocation(tz)
	if err != nil {
		return t, err
	}
	return t.In(loc), nil
}

// ConvertToUTC converts a user's local time to UTC
func (s *TimezoneService) ConvertToUTC(t time.Time, tz string) (time.Time, error) {
	// Ensure the input time is associated with the correct location first
	_, err := s.GetLocation(tz)
	if err != nil {
		return t, err
	}
	
	// Re-interpret the time in the user's location if it's not already
	// This is tricky: if t comes in as UTC but represents "10:00 AM Cairo", we need to tell Go that.
	// However, usually we receive a specific instant.
	// If we want to say "What is 10:00 AM in Cairo as UTC?":
	
	// Assuming t is the instant we want to convert to UTC (it's already an instant)
	return t.UTC(), nil
}
