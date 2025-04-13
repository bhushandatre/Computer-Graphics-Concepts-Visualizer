import streamlit as st
import subprocess
import os

st.set_page_config(page_title="📦 Project Launcher", layout="centered")
st.title("🚀 Graphics Concepts Visualization Simulator")

st.markdown("### Select a Visualization to Simulate:")

col1, col2, col3 = st.columns(3)

# Define the paths to each app
project_paths = {
    "Curve Drawer Simulator": "curve_drawer_project/streamlit_app.py",
    "Hidden Surface Elimination Simulator": "hidden_surface_elimination_v2/app.py",
    "Shading Visualizer Simulator": "shading_project/app.py"
}

# Launch project functions
def launch_project(path):
    if os.path.exists(path):
        subprocess.Popen(["streamlit", "run", path])
        st.success(f"Launched: {path}")
    else:
        st.error(f"File not found: {path}")

# Buttons to launch each project
with col1:
    if st.button("🧱 Curve Drawer Simulator"):
        launch_project(project_paths["Curve Drawer Simulator"])

with col2:
    if st.button("📊 Hidden Surface Elimination Simulator"):
        launch_project(project_paths["Hidden Surface Elimination Simulator"])

with col3:
    if st.button("💬 Shading Visualizer Simulator"):
        launch_project(project_paths["Shading Visualizer Simulator"])
