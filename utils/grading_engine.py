import json
import re

def load_policies():
    try:
        with open('grading_policies.json', 'r') as f:
            return json.load(f)
    except:
        return []

def match_course_policy(course_name, policies):
    """Matches a Classroom course name to a policy using keywords."""
    course_name_lower = course_name.lower()
    
    best_match = None
    max_score = 0
    
    for policy in policies:
        score = 0
        for keyword in policy['keywords']:
            if keyword in course_name_lower:
                score += len(keyword) # Longer keyword match = better score
        
        if score > max_score:
            max_score = score
            best_match = policy
            
    return best_match

def categorize_assignment(title, policy_categories):
    """Matches an assignment title to a policy category (e.g., 'Quiz 1' -> 'Quizzes')."""
    title_lower = title.lower()
    
    # 1. Direct Match
    for category in policy_categories:
        if category.lower() in title_lower:
            return category
            
    # 2. Fuzzy/Synonym Match
    synonyms = {
        "Quizzes": ["quiz", "test"],
        "Assignments": ["assignment", "hw", "homework", "problem set"],
        "Midterm Exam": ["midterm", "mt"],
        "Final Exam": ["final"],
        "Project": ["project", "milestone"],
        "Lab": ["lab"],
        "Lab Exam": ["lab exam", "practical"],
        "Attendance": ["attendance", "participation"]
    }
    
    for category, keywords in synonyms.items():
        if category in policy_categories:
            for keyword in keywords:
                if keyword in title_lower:
                    return category
                    
    return "Uncategorized"

def calculate_weighted_grade(grades, policy):
    """
    Calculates the weighted grade based on the policy and rules.
    grades: list of {'category': 'Quizzes', 'percentage': 85.0}
    """
    total_grade = 0
    total_weight = 0
    
    # Group grades by category
    grouped_grades = {}
    for g in grades:
        cat = g['Category']
        if cat not in grouped_grades:
            grouped_grades[cat] = []
        grouped_grades[cat].append(g['Percentage'])
        
    for category, weight in policy['policy'].items():
        if category in grouped_grades:
            scores = grouped_grades[category]
            
            # Apply Rules (e.g., "best 2 of 3")
            rule = policy.get('rules', {}).get(category)
            if rule:
                if "best" in rule:
                    # Extract N (best N)
                    try:
                        n = int(re.search(r'best (\d+)', rule).group(1))
                        scores.sort(reverse=True)
                        scores = scores[:n]
                    except:
                        pass
            
            # Average the scores for this category
            if scores:
                avg_score = sum(scores) / len(scores)
                total_grade += avg_score * weight
                total_weight += weight
                
    # Normalize if not all categories are graded yet
    if total_weight > 0:
        current_grade = (total_grade / total_weight) * 100
        return current_grade, total_weight * 100
    else:
        return 0, 0
