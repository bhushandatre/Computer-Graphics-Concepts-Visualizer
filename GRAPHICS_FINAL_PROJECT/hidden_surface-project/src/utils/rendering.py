import numpy as np
from PIL import Image, ImageDraw

def render_polygon(draw, vertices, color):
    """Draw a polygon on a PIL ImageDraw object"""
    if len(vertices) >= 3:
        draw.polygon(vertices, fill=color, outline=(255, 255, 255))

def project_point(point, camera_pos, camera_angle, width, height, zoom=1.0):
    """3D to 2D projection with perspective"""
    x = point[0] * np.cos(camera_angle) - point[2] * np.sin(camera_angle)
    z = point[0] * np.sin(camera_angle) + point[2] * np.cos(camera_angle)
    y = point[1]
    
    if z - camera_pos[2] <= 0:
        return None  # Behind camera
    
    scale = 500 * zoom / (z - camera_pos[2])
    px = width // 2 + int(x * scale)
    py = height // 2 - int(y * scale)
    
    return (px, py)

def create_image(width, height, bg_color=(0, 0, 0)):
    """Create a new PIL Image with background"""
    return Image.new('RGB', (width, height), bg_color)