import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from src.algorithms import (
    backface_culling, zbuffer, depth_sort, floating_horizon,
    hierarchical_zbuffer, texture_mapping, transparency
)
from src.objects import cube, sphere, surface, torus, Mesh
from src.lighting import PhongLighting
from src.textures import Texture
import os

# Set up page config
st.set_page_config(
    page_title="3D Hidden Surface Elimination",
    page_icon=":eye:",
    layout="wide"
)

# Sidebar controls
def sidebar_controls():
    st.sidebar.title("Controls")
    
    # Algorithm selection
    algorithm = st.sidebar.selectbox(
        "Rendering Algorithm",
        ["Z-Buffer", "Hierarchical Z-Buffer", "Depth Sort", 
         "Backface Culling", "Floating Horizon", "Texture Mapping", 
         "Transparency"]
    )
    
    # Object selection
    objects = st.sidebar.multiselect(
        "Objects in Scene",
        ["Cube", "Sphere", "Surface", "Torus", "Custom Mesh"],
        default=["Cube", "Sphere"]
    )
    
    # Lighting controls
    st.sidebar.subheader("Lighting")
    light_pos = st.sidebar.slider("Light Position", -10.0, 10.0, (2.0, 5.0, 5.0))
    ambient = st.sidebar.slider("Ambient", 0.0, 1.0, 0.2)
    diffuse = st.sidebar.slider("Diffuse", 0.0, 1.0, 0.7)
    specular = st.sidebar.slider("Specular", 0.0, 1.0, 0.5)
    shininess = st.sidebar.slider("Shininess", 1, 256, 32)
    
    # Camera controls
    st.sidebar.subheader("Camera")
    camera_pos = st.sidebar.slider("Camera Position", -10.0, 10.0, (0.0, 0.0, 0.0))
    camera_angle = st.sidebar.slider("Camera Angle", -np.pi, np.pi, 0.0)
    zoom = st.sidebar.slider("Zoom", 0.1, 2.0, 1.0)
    
    # Texture options
    texture_file = None
    if "Texture Mapping" in algorithm:
        texture_file = st.sidebar.file_uploader("Upload Texture", type=["png", "jpg"])
    
    return {
        "algorithm": algorithm,
        "objects": objects,
        "light_pos": light_pos,
        "ambient": ambient,
        "diffuse": diffuse,
        "specular": specular,
        "shininess": shininess,
        "camera_pos": camera_pos,
        "camera_angle": camera_angle,
        "zoom": zoom,
        "texture_file": texture_file
    }

# Main rendering function
def render_scene(params):
    # Create scene objects
    objects = []
    
    if "Cube" in params["objects"]:
        cube = Cube(position=[-1.5, 0, 5], size=1, color=(255, 0, 0))
        objects.append(cube)
    
    if "Sphere" in params["objects"]:
        sphere = Sphere(position=[1.5, 0, 6], radius=1, color=(0, 0, 255))
        objects.append(sphere)
    
    if "Surface" in params["objects"]:
        surface = Surface(
            function=lambda x, z: np.sin(np.sqrt(x**2 + z**2)) / np.sqrt(x**2 + z**2),
            bounds=(-3, 3, -3, 3),
            color=(0, 255, 0)
        )
        objects.append(surface)
    
    if "Torus" in params["objects"]:
        torus = Torus(position=[0, -1.5, 7], major_radius=1.5, minor_radius=0.5, color=(255, 255, 0))
        objects.append(torus)
    
    # Setup lighting
    lighting = PhongLighting(
        light_position=params["light_pos"],
        ambient=params["ambient"],
        diffuse=params["diffuse"],
        specular=params["specular"],
        shininess=params["shininess"]
    )
    
    # Setup algorithm
    if params["algorithm"] == "Z-Buffer":
        renderer = ZBuffer(width=800, height=600)
    elif params["algorithm"] == "Hierarchical Z-Buffer":
        renderer = HierarchicalZBuffer(width=800, height=600)
    elif params["algorithm"] == "Depth Sort":
        renderer = DepthSort()
    elif params["algorithm"] == "Backface Culling":
        renderer = BackfaceCulling()
    elif params["algorithm"] == "Floating Horizon":
        renderer = FloatingHorizon(width=800, height=600)
    elif params["algorithm"] == "Texture Mapping":
        texture = None
        if params["texture_file"]:
            texture = Texture(params["texture_file"])
        renderer = TextureMapping(width=800, height=600, texture=texture)
    elif params["algorithm"] == "Transparency":
        renderer = Transparency(width=800, height=600)
    
    # Render the scene
    fig, ax = plt.subplots(figsize=(10, 8))
    renderer.render(
        objects=objects,
        camera_pos=params["camera_pos"],
        camera_angle=params["camera_angle"],
        zoom=params["zoom"],
        lighting=lighting
    )
    
    # Display the result
    st.pyplot(fig)
    plt.close(fig)

# Main app
def main():
    st.title("3D Hidden Surface Elimination Visualizer")
    st.write("""
    Explore different algorithms for hidden surface determination in 3D computer graphics.
    Use the controls in the sidebar to change the scene and rendering parameters.
    """)
    
    # Get user parameters
    params = sidebar_controls()
    
    # Render button
    if st.sidebar.button("Render Scene"):
        with st.spinner("Rendering..."):
            render_scene(params)
    else:
        # Show initial scene
        render_scene(params)
    
    # Algorithm explanations
    st.sidebar.markdown("---")
    st.sidebar.subheader("Algorithm Info")
    algorithm_info = {
        "Z-Buffer": "Standard depth buffer algorithm with O(n) complexity per pixel",
        "Hierarchical Z-Buffer": "Optimized Z-buffer using spatial partitioning",
        "Depth Sort": "Painter's algorithm with O(n log n) sorting",
        "Backface Culling": "Simple object-space culling of back-facing polygons",
        "Floating Horizon": "Specialized for mathematical surfaces",
        "Texture Mapping": "Adds texture support to Z-buffer",
        "Transparency": "Handles transparent surfaces with depth sorting"
    }
    st.sidebar.info(algorithm_info[params["algorithm"]])

if __name__ == "__main__":
    main()