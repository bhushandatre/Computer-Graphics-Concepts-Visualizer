import streamlit as st
from rendering.scene import Scene
from rendering.camera import Camera
from rendering.renderer import Renderer

st.set_page_config(layout="wide")
st.title("🔍 Hidden Surface Elimination - 3D Viewer")

if "scene" not in st.session_state:
    st.session_state.scene = Scene()

# Sidebar: Camera Settings
st.sidebar.header("🎥 Camera Settings")
camera_x = st.sidebar.slider("Camera X", -20.0, 20.0, 10.0)
camera_y = st.sidebar.slider("Camera Y", -20.0, 20.0, 10.0)
camera_z = st.sidebar.slider("Camera Z", -20.0, 20.0, 10.0)
look_at_x = st.sidebar.slider("Look At X", -20.0, 20.0, 0.0)
look_at_y = st.sidebar.slider("Look At Y", -20.0, 20.0, 0.0)
look_at_z = st.sidebar.slider("Look At Z", -20.0, 20.0, 0.0)
camera = Camera(position=(camera_x, camera_y, camera_z), look_at=(look_at_x, look_at_y, look_at_z))

# Add object
st.sidebar.header("➕ Add 3D Object")
object_type = st.sidebar.selectbox("Object Type", ["Cube", "Sphere", "Pyramid", "Cone", "Cylinder"])
obj_x = st.sidebar.number_input("X Position", value=0.0)
obj_y = st.sidebar.number_input("Y Position", value=0.0)
obj_z = st.sidebar.number_input("Z Position", value=0.0)
scale = st.sidebar.slider("Scale", 0.1, 5.0, 1.0)
add_obj = st.sidebar.button("Add Object")

if add_obj:
    st.session_state.scene.add_object(object_type, (obj_x, obj_y, obj_z), scale)

# Scene Display
renderer = Renderer(st.session_state.scene, camera)
fig = renderer.render()
st.pyplot(fig)

