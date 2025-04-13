import numpy as np

def calculate_normal(vertices):
    """Calculate normal vector for a polygon face"""
    if len(vertices) < 3:
        return np.array([0, 0, 0])
    
    v1 = np.array(vertices[1]) - np.array(vertices[0])
    v2 = np.array(vertices[2]) - np.array(vertices[0])
    normal = np.cross(v1, v2)
    return normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else normal

def is_backface(vertex, normal, camera_pos):
    """Determine if face is pointing away from camera"""
    view_vector = np.array(camera_pos) - np.array(vertex)
    return np.dot(normal, view_vector) <= 0