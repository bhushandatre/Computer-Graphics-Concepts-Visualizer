import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from streamlit_drawable_canvas import st_canvas
from curve_utils import bezier_curve, bspline_curve, lagrange_interpolation

st.set_page_config(layout="centered")
st.title("🎨 Curve Drawing Simulator with Drag-and-Drop")

# ---- STATE INITIALIZATION ----
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.points = [[50 + i * 50, 50 + i * 50] for i in range(4)]
    st.session_state.curve_type = "Bezier"
    st.session_state.drag_mode = True
    st.session_state.canvas_data = None  # Store only json_data (not full canvas_result)

# ---- SIDEBAR CONTROLS ----
st.sidebar.title("Controls")
st.session_state.curve_type = st.sidebar.selectbox(
    "Select Curve Type",
    ["Bezier", "B-spline", "Lagrange"],
    index=["Bezier", "B-spline", "Lagrange"].index(st.session_state.curve_type)
)
st.session_state.drag_mode = st.sidebar.checkbox("🖱️ Enable Drag Mode", value=st.session_state.drag_mode)

# ---- CANVAS AND POINT HANDLING ----
if st.session_state.drag_mode:
    st.markdown("⬇️ Drag points to reshape the curve:")

    initial_drawing = None
    if st.session_state.canvas_data is None:
        initial_drawing = {
            "objects": [
                {
                    "type": "circle",
                    "left": pt[0],
                    "top": pt[1],
                    "radius": 5,
                    "fill": "red",
                }
                for pt in st.session_state.points
            ]
        }

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 1)",
        stroke_width=0,
        background_color="#FFFFFF",
        update_streamlit=True,
        height=400,
        width=600,
        drawing_mode="transform",
        initial_drawing=initial_drawing,
        key="canvas_drag",
    )

    # Save latest json_data for persistence
    if canvas_result and canvas_result.json_data:
        st.session_state.canvas_data = canvas_result.json_data

    new_points = []
    if st.session_state.canvas_data:
        try:
            new_points = [
                [item["left"], item["top"]]
                for item in st.session_state.canvas_data["objects"]
                if item.get("type") == "circle"
            ]
        except Exception as e:
            st.warning(f"⚠️ Canvas parsing error: {e}")
            new_points = st.session_state.points

    if len(new_points) >= 3:
        st.session_state.points = new_points

else:
    num_points = st.sidebar.slider("Number of Control Points", 3, 10, len(st.session_state.points))
    st.sidebar.write("Enter control points (x, y):")
    new_points = []
    for i in range(num_points):
        x = st.sidebar.number_input(
            f"Point {i+1} - x",
            value=st.session_state.points[i][0] if i < len(st.session_state.points) else 50 + i * 50,
            key=f"x_{i}",
        )
        y = st.sidebar.number_input(
            f"Point {i+1} - y",
            value=st.session_state.points[i][1] if i < len(st.session_state.points) else 50 + i * 50,
            key=f"y_{i}",
        )
        new_points.append([x, y])
    st.session_state.points = new_points
    st.session_state.canvas_data = None  # Reset canvas mode state

# ---- CURVE CALCULATION AND PLOTTING ----
points = np.array(st.session_state.points)

if len(points) >= 3:
    curve = {
        "Bezier": bezier_curve,
        "B-spline": bspline_curve,
        "Lagrange": lagrange_interpolation,
    }[st.session_state.curve_type](points)
else:
    curve = None

fig, ax = plt.subplots()
if len(points) > 0:
    ax.plot(points[:, 0], points[:, 1], "ro--", label="Control Points")
if curve is not None and len(curve) > 0:
    ax.plot(curve[:, 0], curve[:, 1], "b-", label=f"{st.session_state.curve_type} Curve")
ax.set_title(f"{st.session_state.curve_type} Curve")
ax.set_aspect("equal")
ax.legend()
ax.grid(True)
st.pyplot(fig)
