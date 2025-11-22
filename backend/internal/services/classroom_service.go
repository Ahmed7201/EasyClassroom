package services

import (
	"context"
	"time"

	"classroom-assistant-backend/internal/auth"
	"classroom-assistant-backend/internal/models"
	"golang.org/x/oauth2"
	"google.golang.org/api/classroom/v1"
	"google.golang.org/api/option"
)

type ClassroomService struct{}

func NewClassroomService() *ClassroomService {
	return &ClassroomService{}
}

func (s *ClassroomService) getClient(ctx context.Context, token *oauth2.Token) (*classroom.Service, error) {
	client := auth.GetClient(ctx, token)
	return classroom.NewService(ctx, option.WithHTTPClient(client))
}

func (s *ClassroomService) GetCourses(ctx context.Context, token *oauth2.Token) ([]*models.Course, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	resp, err := srv.Courses.List().CourseStates("ACTIVE").Do()
	if err != nil {
		return nil, err
	}

	var courses []*models.Course
	for _, c := range resp.Courses {
		courses = append(courses, &models.Course{
			ID:                 c.Id,
			Name:               c.Name,
			Section:            c.Section,
			DescriptionHeading: c.DescriptionHeading,
			Description:        c.Description,
			Room:               c.Room,
			OwnerID:            c.OwnerId,
			CreationTime:       c.CreationTime,
			UpdateTime:         c.UpdateTime,
			EnrollmentCode:     c.EnrollmentCode,
			CourseState:        c.CourseState,
			AlternateLink:      c.AlternateLink,
			TeacherGroupEmail:  c.TeacherGroupEmail,
			CourseGroupEmail:   c.CourseGroupEmail,
		})
	}

	return courses, nil
}

func (s *ClassroomService) GetCourse(ctx context.Context, token *oauth2.Token, courseID string) (*models.Course, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	c, err := srv.Courses.Get(courseID).Do()
	if err != nil {
		return nil, err
	}

	return &models.Course{
		ID:                 c.Id,
		Name:               c.Name,
		Section:            c.Section,
		DescriptionHeading: c.DescriptionHeading,
		Description:        c.Description,
		Room:               c.Room,
		OwnerID:            c.OwnerId,
		CreationTime:       c.CreationTime,
		UpdateTime:         c.UpdateTime,
		EnrollmentCode:     c.EnrollmentCode,
		CourseState:        c.CourseState,
		AlternateLink:      c.AlternateLink,
		TeacherGroupEmail:  c.TeacherGroupEmail,
		CourseGroupEmail:   c.CourseGroupEmail,
	}, nil
}

func (s *ClassroomService) GetAssignments(ctx context.Context, token *oauth2.Token, courseID string) ([]*models.Assignment, error) {
	srv, err := s.getClient(ctx, token)
	if err != nil {
		return nil, err
	}

	resp, err := srv.Courses.CourseWork.List(courseID).Do()
	if err != nil {
		return nil, err
	}

	var assignments []*models.Assignment
	for _, w := range resp.CourseWork {
		// Convert materials
		var materials []models.Material
		for _, m := range w.Materials {
			mat := models.Material{}
			if m.DriveFile != nil {
				mat.DriveFile = &models.DriveFile{
					ID:            m.DriveFile.DriveFile.Id,
					Title:         m.DriveFile.DriveFile.Title,
					AlternateLink: m.DriveFile.DriveFile.AlternateLink,
					ThumbnailURL:  m.DriveFile.DriveFile.ThumbnailUrl,
				}
			}
			if m.YoutubeVideo != nil {
				mat.YouTubeVideo = &models.YouTubeVideo{
					ID:            m.YoutubeVideo.Id,
					Title:         m.YoutubeVideo.Title,
					AlternateLink: m.YoutubeVideo.AlternateLink,
					ThumbnailURL:  m.YoutubeVideo.ThumbnailUrl,
				}
			}
			if m.Link != nil {
				mat.Link = &models.Link{
					URL:          m.Link.Url,
					Title:        m.Link.Title,
					ThumbnailURL: m.Link.ThumbnailUrl,
				}
			}
			if m.Form != nil {
				mat.Form = &models.Form{
					FormURL:      m.Form.FormUrl,
					ResponseURL:  m.Form.ResponseUrl,
					Title:        m.Form.Title,
					ThumbnailURL: m.Form.ThumbnailUrl,
				}
			}
			materials = append(materials, mat)
		}

		// Calculate deadline
		var deadline *time.Time
		if w.DueDate != nil && w.DueTime != nil {
			t := time.Date(
				int(w.DueDate.Year),
				time.Month(w.DueDate.Month),
				int(w.DueDate.Day),
				int(w.DueTime.Hours),
				int(w.DueTime.Minutes),
				0, 0, time.UTC,
			)
			deadline = &t
		}

		// Infer type using Academic Parser
		parser := NewAcademicParser()
		assignmentType := parser.ParseAssignmentType(w.Title)

		assignments = append(assignments, &models.Assignment{
			ID:            w.Id,
			CourseID:      w.CourseId,
			Title:         w.Title,
			Description:   w.Description,
			Materials:     materials,
			State:         w.State,
			AlternateLink: w.AlternateLink,
			CreationTime:  w.CreationTime,
			UpdateTime:    w.UpdateTime,
			Deadline:      deadline,
			MaxPoints:     w.MaxPoints,
			WorkType:      w.WorkType,
			Type:          assignmentType,
		})
	}

	return assignments, nil
}
