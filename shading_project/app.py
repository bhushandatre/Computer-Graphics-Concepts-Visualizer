import streamlit as st
import numpy as np
import plotly.graph_objects as go
import trimesh
import tempfile
import os

st.set_page_config(layout="wide")
st.title("🌀 3D Object Shading Visualizer")

# Sidebar controls
model = st.sidebar.selectbox("Choose 3D Model", ["Sphere", "Torus", "Cube", "Upload .OBJ"])
shading_type = st.sidebar.selectbox("Shading Type", ["Phong", "Gouraud"])
res = st.sidebar.slider("Resolution (Sphere/Torus only)", 10, 100, 40)

# Light settings
light_x = st.sidebar.slider("Light X", -5.0, 5.0, 2.0)
light_y = st.sidebar.slider("Light Y", -5.0, 5.0, 2.0)
light_z = st.sidebar.slider("Light Z", -5.0, 5.0, 2.0)
light_position = np.array([light_x, light_y, light_z])

light_r = st.sidebar.slider("Light Red", 0, 255, 255)
light_g = st.sidebar.slider("Light Green", 0, 255, 255)
light_b = st.sidebar.slider("Light Blue", 0, 255, 255)
light_color = (light_r, light_g, light_b)

specular_strength = st.sidebar.slider("Specular Strength (Phong only)", 0.0, 2.0, 0.4)
shininess = st.sidebar.slider("Shininess", 1, 100, 20)

animate = st.sidebar.checkbox("Animate Object Rotation", value=True)

# Upload .obj file
uploaded_file = st.sidebar.file_uploader("Upload .obj file", type=["obj"])

# Model generation
def create_model(model, res, file):
    if model == "Sphere":
        u = np.linspace(0, 2*np.pi, res)
        v = np.linspace(0, np.pi, res)
        u, v = np.meshgrid(u, v)
        x = np.cos(u) * np.sin(v)
        y = np.sin(u) * np.sin(v)
        z = np.cos(v)

    elif model == "Torus":
        u = np.linspace(0, 2*np.pi, res)
        v = np.linspace(0, 2*np.pi, res)
        u, v = np.meshgrid(u, v)
        R, r = 1, 0.4
        x = (R + r * np.cos(v)) * np.cos(u)
        y = (R + r * np.cos(v)) * np.sin(u)
        z = r * np.sin(v)

    elif model == "Cube":
        vertices = np.array([
            [-1, -1, -1], [1, -1, -1],
            [1,  1, -1], [-1, 1, -1],
            [-1, -1,  1], [1, -1,  1],
            [1,  1,  1], [-1, 1,  1]
        ])
        faces = np.array([
            [0,1,2],[0,2,3], [4,5,6],[4,6,7],
            [0,1,5],[0,5,4], [2,3,7],[2,7,6],
            [1,2,6],[1,6,5], [0,3,7],[0,7,4]
        ])
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]
        return x, y, z, faces

    elif model == "Upload .OBJ" and file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".obj") as tmp:
            tmp.write(file.read())
            mesh = trimesh.load(tmp.name)
            os.unlink(tmp.name)
            if not mesh.is_watertight:
                st.warning("The uploaded mesh is not watertight and may not shade correctly.")
            verts = mesh.vertices
            faces = mesh.faces
            return verts[:, 0], verts[:, 1], verts[:, 2], faces

    else:
        return None, None, None, None

    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    faces = []
    for i in range(res - 1):
        for j in range(res - 1):
            idx = i * res + j
            faces.append([idx, idx + 1, idx + res])
            faces.append([idx + 1, idx + res + 1, idx + res])
    return x, y, z, np.array(faces)

def compute_normals(x, y, z, faces):
    v0 = np.stack([x[faces[:, 0]], y[faces[:, 0]], z[faces[:, 0]]], axis=-1)
    v1 = np.stack([x[faces[:, 1]], y[faces[:, 1]], z[faces[:, 1]]], axis=-1)
    v2 = np.stack([x[faces[:, 2]], y[faces[:, 2]], z[faces[:, 2]]], axis=-1)
    normals = np.cross(v1 - v0, v2 - v0)
    norms = np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-9
    return normals / norms

def compute_vertex_normals(x, y, z, faces):
    normals = np.zeros((len(x), 3))
    face_normals = compute_normals(x, y, z, faces)
    for i, face in enumerate(faces):
        for v in face:
            normals[v] += face_normals[i]
    norms = np.linalg.norm(normals, axis=-1, keepdims=True) + 1e-9
    return normals / norms

def phong_shading(x, y, z, faces, light_pos, light_color, specular_strength, shininess):
    face_normals = compute_normals(x, y, z, faces)
    centers = np.stack([x[faces].mean(axis=1),
                        y[faces].mean(axis=1),
                        z[faces].mean(axis=1)], axis=-1)
    L = light_pos - centers
    L /= np.linalg.norm(L, axis=-1, keepdims=True)
    V = -centers
    V /= np.linalg.norm(V, axis=-1, keepdims=True)
    R = 2 * (np.sum(face_normals * L, axis=-1, keepdims=True) * face_normals) - L
    R /= np.linalg.norm(R, axis=-1, keepdims=True)
    diffuse = np.clip((face_normals * L).sum(axis=-1), 0, 1)
    specular = np.clip((R * V).sum(axis=-1), 0, 1) ** shininess
    intensity = np.clip(diffuse + specular_strength * specular, 0, 1)
    color = ['rgb({},{},{})'.format(*(int(c*i) for c in light_color)) for i in intensity]
    return color

def gouraud_shading(x, y, z, faces, light_pos, light_color):
    normals = compute_vertex_normals(x, y, z, faces)
    verts = np.stack([x, y, z], axis=-1)
    light_vecs = light_pos - verts
    light_vecs /= np.linalg.norm(light_vecs, axis=-1, keepdims=True)
    intensity = np.clip((normals * light_vecs).sum(axis=-1), 0, 1)
    return intensity

# Create model
x, y, z, faces = create_model(model, res, uploaded_file)
if x is None or faces is None:
    st.error("Could not load or create model.")
    st.stop()

# Apply shading
if shading_type == "Phong":
    face_colors = phong_shading(x, y, z, faces, light_position, light_color, specular_strength, shininess)
    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        facecolor=face_colors,
        flatshading=True,
        lighting=dict(ambient=0.2, diffuse=0.7),
        showscale=False
    )
else:
    intensity = gouraud_shading(x, y, z, faces, light_position, light_color)
    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=faces[:, 0], j=faces[:, 1], k=faces[:, 2],
        intensity=intensity,
        colorscale="Viridis",
        flatshading=False,
        showscale=False
    )

# Animate object rotation
if animate:
    angle = st.session_state.get("angle", 0)
    angle += 0.03
    st.session_state["angle"] = angle
    cam_eye = dict(
        x=np.cos(angle)*2,
        y=np.sin(angle)*2,
        z=np.sin(angle/2)*2
    )
else:
    cam_eye = dict(x=1.5, y=1.5, z=1.5)

fig = go.Figure(data=[mesh])
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    scene_camera=dict(eye=cam_eye),
    scene=dict(aspectmode="data")
)
st.plotly_chart(fig, use_container_width=True)
