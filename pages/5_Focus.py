import streamlit as st
import time
from utils.styles import load_css, card

st.set_page_config(page_title="Focus Mode", page_icon="🍅", layout="wide")
load_css()

def main():
    st.title("🍅 Focus Timer")
    
    # Session State for Timer
    if 'timer_active' not in st.session_state:
        st.session_state.timer_active = False
    if 'time_left' not in st.session_state:
        st.session_state.time_left = 25 * 60
    if 'timer_mode' not in st.session_state:
        st.session_state.timer_mode = "Work"

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Timer Controls")
        
        # Mode Selection
        mode = st.radio("Mode", ["Work (25m)", "Short Break (5m)", "Long Break (15m)"], horizontal=True)
        
        if mode == "Work (25m)" and st.session_state.timer_mode != "Work":
            st.session_state.time_left = 25 * 60
            st.session_state.timer_mode = "Work"
            st.session_state.timer_active = False
        elif mode == "Short Break (5m)" and st.session_state.timer_mode != "Short":
            st.session_state.time_left = 5 * 60
            st.session_state.timer_mode = "Short"
            st.session_state.timer_active = False
        elif mode == "Long Break (15m)" and st.session_state.timer_mode != "Long":
            st.session_state.time_left = 15 * 60
            st.session_state.timer_mode = "Long"
            st.session_state.timer_active = False

        # Timer Display
        mins, secs = divmod(st.session_state.time_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        st.markdown(f"""
        <div style="text-align: center; font-size: 5rem; font-weight: 700; color: #bd93f9; margin: 20px 0;">
            {time_str}
        </div>
        """, unsafe_allow_html=True)

        # Controls
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("▶ Start", use_container_width=True):
                st.session_state.timer_active = True
        with c2:
            if st.button("⏸ Pause", use_container_width=True):
                st.session_state.timer_active = False
        with c3:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timer_active = False
                if st.session_state.timer_mode == "Work":
                    st.session_state.time_left = 25 * 60
                elif st.session_state.timer_mode == "Short":
                    st.session_state.time_left = 5 * 60
                else:
                    st.session_state.time_left = 15 * 60

        # Timer Logic
        if st.session_state.timer_active:
            if st.session_state.time_left > 0:
                time.sleep(1)
                st.session_state.time_left -= 1
                st.rerun()
            else:
                st.session_state.timer_active = False
                st.balloons()
                st.success("Timer Complete!")

    with col2:
        st.subheader("📝 Session Tasks")
        
        if 'tasks' not in st.session_state:
            st.session_state.tasks = []

        new_task = st.text_input("Add a task for this session")
        if st.button("Add Task") and new_task:
            st.session_state.tasks.append({"name": new_task, "done": False})
            st.rerun()

        for i, task in enumerate(st.session_state.tasks):
            cols = st.columns([0.1, 0.9])
            with cols[0]:
                done = st.checkbox("", value=task['done'], key=f"task_{i}")
            with cols[1]:
                st.markdown(f"<div style='font-size:1.2rem; text-decoration: {'line-through' if done else 'none'}'>{task['name']}</div>", unsafe_allow_html=True)
            
            st.session_state.tasks[i]['done'] = done

        if st.button("Clear Completed"):
            st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
            st.rerun()

if __name__ == "__main__":
    main()
