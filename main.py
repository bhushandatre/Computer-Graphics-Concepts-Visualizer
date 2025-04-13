import streamlit as st

st.set_page_config(page_title="Computer Graphics Dashboard", layout="wide")
st.title("🎨 Computer Graphics Final Project")
st.markdown("Use the sidebar to navigate between different visual demos.")

page = st.sidebar.radio(
    "Select a module:",
    ("Curve Drawer", "Shading", "Hidden Surface Elimination")
)

if page == "Curve Drawer":
    try:
        from curve_drawer_project.streamlit_app import run as run_curve
        run_curve()
    except Exception as e:
        st.error(f"Error loading Curve Drawer module: {e}")

elif page == "Shading":
    try:
        from shading_project.app import run as run_shading
        run_shading()
    except Exception as e:
        st.error(f"Error loading Shading module: {e}")

elif page == "Hidden Surface Elimination":
    try:
        from hidden_surface_elimination_v2.app import run as run_hidden
        run_hidden()
    except Exception as e:
        st.error(f"Error loading Hidden Surface Elimination module: {e}")