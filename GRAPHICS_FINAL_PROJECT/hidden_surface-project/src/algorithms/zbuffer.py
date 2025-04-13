import numpy as np
import pygame
from utils.math_utils import calculate_normal, is_backface

class ZBuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset_buffers()
    
    def reset_buffers(self):
        self.z_buffer = np.full((self.width, self.height), np.inf)
        self.color_buffer = np.zeros((self.width, self.height, 3))
    
    def render(self, screen, objects, camera_pos, camera_angle):
        self.reset_buffers()
        width, height = self.width, self.height
        
        for obj in objects:
            if hasattr(obj, 'faces'):
                # Process polygonal objects
                for face in obj.faces:
                    world_vertices = [obj.get_vertex(i) for i in face]
                    normal = calculate_normal(world_vertices)
                    
                    if is_backface(world_vertices[0], normal, camera_pos):
                        continue
                    
                    self.process_face(world_vertices, obj.color, camera_pos, camera_angle)
            elif hasattr(obj, 'function'):
                # Process mathematical surfaces
                self.process_surface(obj, camera_pos, camera_angle)
        
        # Convert color buffer to Pygame surface
        surf = pygame.surfarray.make_surface((self.color_buffer * 255).astype(np.uint8))
        screen.blit(surf, (0, 0))
    
    def process_face(self, vertices, color, camera_pos, camera_angle):
        # Project vertices and create 2D polygon
        projected = []
        depths = []
        for vertex in vertices:
            x = vertex[0] * np.cos(camera_angle) - vertex[2] * np.sin(camera_angle)
            z = vertex[0] * np.sin(camera_angle) + vertex[2] * np.cos(camera_angle)
            y = vertex[1]
            
            if z - camera_pos[2] <= 0:
                return
                
            scale = 500 / (z - camera_pos[2])
            px = self.width // 2 + int(x * scale)
            py = self.height // 2 - int(y * scale)
            projected.append((px, py))
            depths.append(z)
        
        if len(projected) < 3:
            return
        
        # Get bounding box
        min_x = max(0, min(p[0] for p in projected))
        max_x = min(self.width - 1, max(p[0] for p in projected))
        min_y = max(0, min(p[1] for p in projected))
        max_y = min(self.height - 1, max(p[1] for p in projected))
        
        # Rasterize the polygon
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if self.point_in_polygon(x, y, projected):
                    # Calculate barycentric coordinates to get depth
                    z = self.interpolate_depth(x, y, projected, depths)
                    
                    if z < self.z_buffer[x, y]:
                        self.z_buffer[x, y] = z
                        self.color_buffer[x, y] = np.array(color) / 255
    
    def process_surface(self, surface, camera_pos, camera_angle):
        # Sample the surface function and render points
        x_min, x_max, z_min, z_max = surface.bounds
        step = 0.1
        
        for x in np.arange(x_min, x_max, step):
            for z in np.arange(z_min, z_max, step):
                try:
                    y = surface.function(x, z)
                    vertex = np.array([x, y, z])
                    
                    # Transform and project
                    tx = vertex[0] * np.cos(camera_angle) - vertex[2] * np.sin(camera_angle)
                    tz = vertex[0] * np.sin(camera_angle) + vertex[2] * np.cos(camera_angle)
                    ty = vertex[1]
                    
                    if tz - camera_pos[2] <= 0:
                        continue
                        
                    scale = 500 / (tz - camera_pos[2])
                    px = int(self.width // 2 + tx * scale)
                    py = int(self.height // 2 - ty * scale)
                    
                    if 0 <= px < self.width and 0 <= py < self.height:
                        if tz < self.z_buffer[px, py]:
                            self.z_buffer[px, py] = tz
                            self.color_buffer[px, py] = np.array(surface.color) / 255
                except:
                    continue
    
    def point_in_polygon(self, x, y, polygon):
        # Ray casting algorithm
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def interpolate_depth(self, x, y, polygon, depths):
        # Barycentric interpolation for depth
        # Simplified version - just average for this demo
        return sum(depths) / len(depths)