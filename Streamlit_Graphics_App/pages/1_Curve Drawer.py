import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from streamlit_drawable_canvas import st_canvas
from utils.curve_utils import bezier_curve, bspline_curve, lagrange_interpolation


st.set_page_config(layout="centered")
st.title("🎨 Curve Drawing Simulator with Drag-and-Drop")

# Sidebar Controls
st.sidebar.title("Controls")
curve_type = st.sidebar.selectbox("Select Curve Type", ["Bezier", "B-spline", "Lagrange"])
drag_mode = st.sidebar.checkbox("🖱️ Enable Drag Mode", value=False)

# Store default or previous control points
if "points" not in st.session_state:
    st.session_state.points = [[i * 30, i * 30] for i in range(4)]

# If not in drag mode, show manual entry
if not drag_mode:
    num_points = st.sidebar.slider("Number of Control Points", 3, 10, len(st.session_state.points))
    new_points = []
    st.sidebar.write("Enter control points (x, y):")
    for i in range(num_points):
        x = st.sidebar.number_input(f"Point {i+1} - x", value=st.session_state.points[i][0] if i < len(st.session_state.points) else i*30, key=f"x_{i}")
        y = st.sidebar.number_input(f"Point {i+1} - y", value=st.session_state.points[i][1] if i < len(st.session_state.points) else i*30, key=f"y_{i}")
        new_points.append([x, y])
    st.session_state.points = new_points

# If in drag mode, show canvas
else:
    st.markdown("⬇️ Drag points to reshape the curve:")
    # Create canvas with draggable circles
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 1)", 
        stroke_width=0,
        background_color="#FFFFFF",
        update_streamlit=True,
        height=400,
        width=600,
        drawing_mode="transform",  # makes it draggable
        initial_drawing=[
            {
                "type": "circle",
                "left": pt[0],
                "top": pt[1],
                "radius": 5,
                "fill": "red",
            }
            for pt in st.session_state.points
        ],
        key="canvas_drag"
    )

    # Extract updated positions
    new_points = []
    if canvas_result.json_data is not None:
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "circle":
                x, y = obj["left"], obj["top"]
                new_points.append([x, y])
    if len(new_points) >= 3:
        st.session_state.points = new_points

# Convert to NumPy array
points = np.array(st.session_state.points)

# Draw selected curve
if len(points) >= 3:
    if curve_type == "Bezier":
        curve = bezier_curve(points)
    elif curve_type == "B-spline":
        curve = bspline_curve(points)
    elif curve_type == "Lagrange":
        curve = lagrange_interpolation(points)
else:
    curve = None

# Plot the result
fig, ax = plt.subplots()
if len(points) > 0:
    ax.plot(points[:, 0], points[:, 1], 'ro--', label="Control Points")
if curve is not None and len(curve) > 0:
    ax.plot(curve[:, 0], curve[:, 1], 'b-', label=f"{curve_type} Curve")
ax.set_title(f"{curve_type} Curve")
ax.set_aspect('equal')
ax.legend()
ax.grid(True)
st.pyplot(fig)
