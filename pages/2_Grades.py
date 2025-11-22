import streamlit as st
import pandas as pd
import plotly.express as px
from auth import authenticate
from api.classroom import ClassroomClient
from api.gmail import GmailClient
from utils.styles import load_css, card
from utils.grading_engine import load_policies, match_course_policy, categorize_assignment, calculate_weighted_grade

st.set_page_config(page_title="Grades", page_icon="📈", layout="wide")
load_css()

def main():
    st.title("📈 Grade Analytics")
    
    creds = authenticate()
    if not creds:
        st.error("Please log in first.")
        return

    client = ClassroomClient(creds)
    gmail_client = GmailClient(creds)
    
    # 1. Fetch Courses First
    courses = client.get_courses()
    if not courses:
        st.warning("No courses found.")
        return

    # 2. Course Selector
    selected_course_name = st.selectbox("Select Course to Analyze", [c['name'] for c in courses])
    selected_course = next(c for c in courses if c['name'] == selected_course_name)

    # 3. Fetch Grades & Apply Policy
    policies = load_policies()
    matched_policy = match_course_policy(selected_course_name, policies)
    
    with st.spinner(f"Fetching grades for {selected_course_name}..."):
        works = client.get_course_work(selected_course['id'])
        course_grades = []
        
        for work in works:
            if work['max_points']:
                sub = client.get_my_submissions(selected_course['id'], work['id'])
                if sub and sub.get('assigned_grade'):
                    # Categorize
                    category = "Uncategorized"
                    if matched_policy:
                        category = categorize_assignment(work['title'], matched_policy['policy'].keys())
                    
                    course_grades.append({
                        'Assignment': work['title'],
                        'Category': category,
                        'Grade': sub['assigned_grade'],
                        'Max': work['max_points'],
                        'Percentage': (sub['assigned_grade'] / work['max_points']) * 100
                    })

    if not course_grades:
        st.info(f"No graded assignments found for {selected_course_name} yet.")
        return

    df = pd.DataFrame(course_grades)

    # 4. Display Stats & Charts
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Weighted Grade Calculation
        if matched_policy:
            st.success(f"✅ Matched Policy: {', '.join(matched_policy['keywords'][:2])}...")
            current_grade, weight_used = calculate_weighted_grade(course_grades, matched_policy)
            st.metric("Projected Grade", f"{current_grade:.1f}%", delta=f"Based on {weight_used:.0f}% of syllabus")
            
            # Show Policy Breakdown
            with st.expander("📜 Grading Policy"):
                for cat, weight in matched_policy['policy'].items():
                    rule = matched_policy.get('rules', {}).get(cat, "")
                    st.write(f"- **{cat}**: {weight*100:.0f}% {f'({rule})' if rule else ''}")
        else:
            st.warning("⚠️ No matching grading policy found.")
            avg = df['Percentage'].mean()
            st.metric("Simple Average", f"{avg:.1f}%")
        
        # Chart by Category
        if matched_policy:
            fig = px.box(df, x='Category', y='Percentage', title="Performance by Category", color='Category')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Detailed Grades")
        for idx, grade in enumerate(course_grades):
            with st.expander(f"{grade['Assignment']} ({grade['Grade']}/{grade['Max']}) - {grade['Category']}"):
                st.progress(grade['Percentage'] / 100)
                st.write(f"**Percentage:** {grade['Percentage']:.1f}%")
                
                if st.button("🚨 Dispute / Ask TA", key=f"dispute_{grade['Assignment']}_{idx}"):
                    teachers = client.get_teachers(selected_course['id'], selected_course_name)
                    if not teachers:
                        st.error("Could not find teacher emails.")
                    else:
                        st.write("Select recipient:")
                        for teacher in teachers:
                            name = teacher.get('profile', {}).get('name', {}).get('fullName', 'Unknown')
                            email = teacher.get('profile', {}).get('emailAddress')
                            photo_url = teacher.get('profile', {}).get('photoUrl', '')
                            
                            t_col1, t_col2 = st.columns([0.15, 0.85])
                            with t_col1:
                                if photo_url:
                                    if not photo_url.startswith('http'):
                                        photo_url = f"https:{photo_url}"
                                    if '/s' in photo_url:
                                        photo_url = photo_url.split('/s')[0] + '/s100-c'
                                    st.markdown(f'<img src="{photo_url}" style="border-radius: 50%; width: 40px; height: 40px; object-fit: cover;">', unsafe_allow_html=True)
                                else:
                                    st.markdown('<div style="font-size: 24px; text-align: center;">👤</div>', unsafe_allow_html=True)
                            
                            with t_col2:
                                if st.button(f"📧 Email {name}", key=f"email_{email}_{idx}"):
                                    subject = f"Question regarding grade for {grade['Assignment']}"
                                    body = f"Dear {name},\n\nI am writing to ask about my grade for {grade['Assignment']} ({grade['Grade']}/{grade['Max']}).\n\n[Write your question here]\n\nBest regards,"
                                    
                                    draft = gmail_client.create_draft(email, subject, body)
                                    if draft:
                                        st.success("Draft created in Gmail!")
                                    else:
                                        st.error("Failed to create draft.")

if __name__ == "__main__":
    main()
