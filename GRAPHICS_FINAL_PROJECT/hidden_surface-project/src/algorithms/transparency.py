import numpy as np
from .depth_sort import DepthSort

class Transparency(DepthSort):
    def __init__(self, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.color_buffer = np.zeros((width, height, 4))  # RGBA
    
    def render(self, screen, objects, camera_pos, camera_angle, lighting=None):
        self.color_buffer.fill(0)
        
        # Separate opaque and transparent objects
        opaque_objs = [obj for obj in objects if not getattr(obj, 'transparent', False)]
        transparent_objs = [obj for obj in objects if getattr(obj, 'transparent', False)]
        
        # First render opaque objects with Z-buffer
        zbuffer = np.full((self.width, self.height), np.inf)
        
        for obj in opaque_objs:
            if hasattr(obj, 'faces'):
                for face in obj.faces:
                    self.render_face(obj, face, zbuffer, camera_pos, camera_angle, lighting)
        
        # Then render transparent objects with depth sorting
        for obj in transparent_objs:
            if hasattr(obj, 'faces'):
                for face in obj.faces:
                    self.render_transparent_face(obj, face, zbuffer, camera_pos, camera_angle, lighting)
        
        # Convert to image
        img = (self.color_buffer * 255).astype(np.uint8)
        plt.imshow(img)
        plt.axis('off')
    
    def render_face(self, obj, face, zbuffer, camera_pos, camera_angle, lighting):
        vertices = [obj.get_vertex(i) for i in face]
        normal = self.calculate_normal(vertices)
        
        if self.is_backface(vertices[0], normal, camera_pos):
            return
        
        # Project vertices
        projected = []
        depths = []
        for vertex in vertices:
            px, py, z = self.project_point(vertex, camera_pos, camera_angle)
            projected.append((px, py))
            depths.append(z)
        
        if len(projected) < 3:
            return
        
        # Rasterize
        min_x = max(0, min(p[0] for p in projected))
        max_x = min(self.width - 1, max(p[0] for p in projected))
        min_y = max(0, min(p[1] for p in projected))
        max_y = min(self.height - 1, max(p[1] for p in projected))
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if self.point_in_polygon(x, y, projected):
                    z = self.interpolate_depth(x, y, projected, depths)
                    
                    if z < zbuffer[x, y]:
                        zbuffer[x, y] = z
                        
                        if lighting:
                            color = lighting.apply(obj.color, normal, camera_pos - np.mean(vertices, axis=0))
                        else:
                            color = obj.color
                        
                        self.color_buffer[x, y, :3] = np.array(color) / 255
                        self.color_buffer[x, y, 3] = 1.0  # Alpha
    
    def render_transparent_face(self, obj, face, zbuffer, camera_pos, camera_angle, lighting):
        vertices = [obj.get_vertex(i) for i in face]
        normal = self.calculate_normal(vertices)
        
        if self.is_backface(vertices[0], normal, camera_pos):
            return
        
        # Project vertices
        projected = []
        depths = []
        for vertex in vertices:
            px, py, z = self.project_point(vertex, camera_pos, camera_angle)
            projected.append((px, py))
            depths.append(z)
        
        if len(projected) < 3:
            return
        
        # Rasterize with blending
        min_x = max(0, min(p[0] for p in projected))
        max_x = min(self.width - 1, max(p[0] for p in projected))
        min_y = max(0, min(p[1] for p in projected))
        max_y = min(self.height - 1, max(p[1] for p in projected))
        
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if self.point_in_polygon(x, y, projected):
                    z = self.interpolate_depth(x, y, projected, depths)
                    
                    # Only render if behind existing geometry (for correct blending)
                    if z > zbuffer[x, y]:
                        continue
                    
                    if lighting:
                        color = lighting.apply(obj.color, normal, camera_pos - np.mean(vertices, axis=0))
                    else:
                        color = obj.color
                    
                    # Alpha blending
                    alpha = getattr(obj, 'alpha', 0.5)
                    new_color = np.array(color) / 255
                    self.color_buffer[x, y, :3] = (
                        alpha * new_color + 
                        (1 - alpha) * self.color_buffer[x, y, :3]
                    )
                    self.color_buffer[x, y, 3] = 1.0  # Reset alpha
    
    def project_point(self, vertex, camera_pos, camera_angle):
        x = vertex[0] * np.cos(camera_angle) - vertex[2] * np.sin(camera_angle)
        z = vertex[0] * np.sin(camera_angle) + vertex[2] * np.cos(camera_angle)
        y = vertex[1]
        
        if z - camera_pos[2] <= 0:
            return -1, -1, np.inf
            
        scale = 500 / (z - camera_pos[2])
        px = self.width // 2 + int(x * scale)
        py = self.height // 2 - int(y * scale)
        
        return px, py, z