package services

import (
	"strings"
)

type AcademicParser struct{}

func NewAcademicParser() *AcademicParser {
	return &AcademicParser{}
}

func (p *AcademicParser) ParseAssignmentType(title string) string {
	titleLower := strings.ToLower(title)

	if strings.Contains(titleLower, "quiz") {
		return "QUIZ"
	} else if strings.Contains(titleLower, "exam") {
		return "EXAM"
	} else if strings.Contains(titleLower, "lab") {
		return "LAB"
	} else if strings.Contains(titleLower, "project") {
		return "PROJECT"
	} else if strings.Contains(titleLower, "midterm") {
		return "MIDTERM"
	} else if strings.Contains(titleLower, "final") {
		return "FINAL"
	} else if strings.Contains(titleLower, "homework") || strings.Contains(titleLower, "hw") {
		return "HOMEWORK"
	}

	return "ASSIGNMENT"
}

func (p *AcademicParser) InferTopic(title, description string) string {
	// Simple keyword extraction for now
	// In a real app, this could be more sophisticated (NLP, etc.)
	
	content := strings.ToLower(title + " " + description)
	
	keywords := []string{
		"python", "java", "c++", "javascript", "react", "sql", "database",
		"algorithm", "structure", "network", "security", "ai", "ml",
	}

	for _, kw := range keywords {
		if strings.Contains(content, kw) {
			return strings.Title(kw)
		}
	}

	return "General"
}
