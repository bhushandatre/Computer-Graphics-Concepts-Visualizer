import numpy as np
import pygame
from utils.math_utils import calculate_normal, is_backface

class DepthSort:
    def render(self, screen, objects, camera_pos, camera_angle):
        width, height = screen.get_size()
        
        # Collect all faces from all objects
        all_faces = []
        for obj in objects:
            if hasattr(obj, 'faces'):
                for face in obj.faces:
                    world_vertices = [obj.get_vertex(i) for i in face]
                    normal = calculate_normal(world_vertices)
                    
                    if is_backface(world_vertices[0], normal, camera_pos):
                        continue
                    
                    # Calculate average depth
                    avg_depth = sum(v[2] for v in world_vertices) / len(world_vertices)
                    all_faces.append((avg_depth, world_vertices, obj.color))
        
        # Sort faces by depth (farthest first)
        all_faces.sort(key=lambda x: -x[0])
        
        # Render from back to front
        for depth, vertices, color in all_faces:
            projected = []
            for vertex in vertices:
                x = vertex[0] * np.cos(camera_angle) - vertex[2] * np.sin(camera_angle)
                z = vertex[0] * np.sin(camera_angle) + vertex[2] * np.cos(camera_angle)
                y = vertex[1]
                
                if z - camera_pos[2] <= 0:
                    break
                    
                scale = 500 / (z - camera_pos[2])
                px = width // 2 + int(x * scale)
                py = height // 2 - int(y * scale)
                projected.append((px, py))
            
            if len(projected) >= 3:
                pygame.draw.polygon(screen, color, projected)
                pygame.draw.polygon(screen, (255, 255, 255), projected, 1)