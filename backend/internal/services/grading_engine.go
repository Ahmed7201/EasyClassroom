package services

import (
	"encoding/json"
	"os"
	"strings"

	"classroom-assistant-backend/internal/models"
	"github.com/lithammer/fuzzysearch/fuzzy"
)

type GradingEngine struct {
	Policies map[string][]models.GradeCategory
}

func NewGradingEngine() *GradingEngine {
	engine := &GradingEngine{
		Policies: make(map[string][]models.GradeCategory),
	}
	engine.loadPolicies()
	return engine
}

func (e *GradingEngine) loadPolicies() {
	// In a real app, this would load from DB or a config file
	// For migration, we'll try to load from the existing JSON if available
	// or use hardcoded defaults matching the Python version
	
	data, err := os.ReadFile("../grading_policies.json")
	if err == nil {
		var policies map[string][]models.GradeCategory
		if err := json.Unmarshal(data, &policies); err == nil {
			e.Policies = policies
			return
		}
	}

	// Fallback defaults
	e.Policies = map[string][]models.GradeCategory{
		"default": {
			{Name: "Assignments", Weight: 30},
			{Name: "Quizzes", Weight: 20},
			{Name: "Midterm", Weight: 20},
			{Name: "Final", Weight: 30},
		},
		"math": {
			{Name: "Homework", Weight: 20},
			{Name: "Quizzes", Weight: 20},
			{Name: "Midterm", Weight: 25},
			{Name: "Final", Weight: 35},
		},
		"cs": {
			{Name: "Labs", Weight: 20},
			{Name: "Project", Weight: 30},
			{Name: "Midterm", Weight: 20},
			{Name: "Final", Weight: 30},
		},
	}
}

func (e *GradingEngine) GetPolicyForCourse(courseName string) []models.GradeCategory {
	// Normalize course name
	name := strings.ToLower(courseName)

	// Exact match first
	if policy, ok := e.Policies[name]; ok {
		return policy
	}

	// Fuzzy match keys
	keys := make([]string, 0, len(e.Policies))
	for k := range e.Policies {
		keys = append(keys, k)
	}

	matches := fuzzy.RankFind(name, keys)
	if len(matches) > 0 {
		// Sort by distance (closest first)
		// RankFind already sorts by distance
		return e.Policies[matches[0].Target]
	}

	return e.Policies["default"]
}

func (e *GradingEngine) CalculateGrades(courseName string, assignments []*models.Assignment) map[string]interface{} {
	policy := e.GetPolicyForCourse(courseName)
	
	// Initialize categories
	categories := make(map[string]*models.GradeCategory)
	for _, p := range policy {
		cat := p // Copy
		cat.Grades = []models.GradeItem{}
		categories[strings.ToLower(p.Name)] = &cat
	}

	// Categorize assignments
	for _, a := range assignments {
		if a.MaxPoints == 0 {
			continue
		}

		// Determine category based on title/type
		catName := "assignments" // Default
		title := strings.ToLower(a.Title)
		
		if strings.Contains(title, "quiz") {
			catName = "quizzes"
		} else if strings.Contains(title, "midterm") {
			catName = "midterm"
		} else if strings.Contains(title, "final") {
			catName = "final"
		} else if strings.Contains(title, "lab") {
			catName = "labs"
		} else if strings.Contains(title, "project") {
			catName = "project"
		} else if strings.Contains(title, "homework") || strings.Contains(title, "hw") {
			catName = "homework"
		}

		// Find best matching category
		if _, ok := categories[catName]; !ok {
			// Try to find closest category name
			catKeys := make([]string, 0, len(categories))
			for k := range categories {
				catKeys = append(catKeys, k)
			}
			matches := fuzzy.RankFind(catName, catKeys)
			if len(matches) > 0 {
				catName = matches[0].Target
			} else {
				catName = "assignments" // Fallback
				if _, ok := categories["assignments"]; !ok {
					// If no assignments category, pick the first one
					for k := range categories {
						catName = k
						break
					}
				}
			}
		}

		// Add to category
		if cat, ok := categories[catName]; ok {
			// In a real app, we'd fetch the user's submission score
			// For now, we'll simulate or just list the max points
			cat.Grades = append(cat.Grades, models.GradeItem{
				Name:     a.Title,
				MaxScore: int(a.MaxPoints),
				DueDate:  a.Deadline.Format("2006-01-02"),
			})
		}
	}

	// Calculate totals
	var totalWeightedScore float64
	var totalWeightUsed float64

	results := make(map[string]interface{})
	categoryResults := []map[string]interface{}{}

	for _, cat := range categories {
		var catTotal float64
		var catMax float64
		
		for _, g := range cat.Grades {
			// Simulate score (e.g., 90%)
			// In real app, use actual score
			score := float64(g.MaxScore) * 0.9 
			catTotal += score
			catMax += float64(g.MaxScore)
		}

		var percentage float64
		if catMax > 0 {
			percentage = (catTotal / catMax) * 100
		}

		weightedScore := (percentage / 100) * cat.Weight
		
		if catMax > 0 {
			totalWeightedScore += weightedScore
			totalWeightUsed += cat.Weight
		}

		categoryResults = append(categoryResults, map[string]interface{}{
			"name":       cat.Name,
			"weight":     cat.Weight,
			"score":      catTotal,
			"max":        catMax,
			"percentage": percentage,
			"items":      len(cat.Grades),
		})
	}

	currentGrade := 0.0
	if totalWeightUsed > 0 {
		currentGrade = (totalWeightedScore / totalWeightUsed) * 100
	}

	results["categories"] = categoryResults
	results["currentGrade"] = currentGrade
	results["projectedGrade"] = totalWeightedScore // Assuming 0 for remaining

	return results
}
