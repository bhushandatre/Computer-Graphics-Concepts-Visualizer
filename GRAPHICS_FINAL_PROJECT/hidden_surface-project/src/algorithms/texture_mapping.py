import numpy as np
from .zbuffer import ZBuffer
from src.textures import Texture

class TextureMapping(ZBuffer):
    def __init__(self, width, height, texture=None):
        super().__init__(width, height)
        self.texture = texture or Texture.default()
    
    def process_face(self, vertices, color, camera_pos, camera_angle, lighting=None):
        if len(vertices) < 3:
            return
            
        # Calculate texture coordinates (simple planar projection)
        tex_coords = []
        for i, vertex in enumerate(vertices):
            # Simple UV mapping based on vertex positions
            u = (vertex[0] - min(v[0] for v in vertices)) / (max(v[0] for v in vertices) - min(v[0] for v in vertices))
            v = (vertex[1] - min(v[1] for v in vertices)) / (max(v[1] for v in vertices) - min(v[1] for v in vertices))
            tex_coords.append((u, v))
        
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
        
        # Rasterize the polygon with texture mapping
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if self.point_in_polygon(x, y, projected):
                    # Calculate barycentric coordinates for interpolation
                    u, v = self.interpolate_texture(x, y, projected, tex_coords)
                    
                    # Get texture color
                    tex_color = self.texture.sample(u, v)
                    
                    # Calculate depth
                    z = self.interpolate_depth(x, y, projected, depths)
                    
                    if z < self.z_buffer[x, y]:
                        self.z_buffer[x, y] = z
                        
                        # Apply lighting if available
                        if lighting:
                            normal = self.calculate_normal(vertices)
                            view_vector = camera_pos - np.mean(vertices, axis=0)
                            lit_color = lighting.apply(tex_color, normal, view_vector)
                            self.color_buffer[x, y] = np.array(lit_color) / 255
                        else:
                            self.color_buffer[x, y] = np.array(tex_color) / 255
    
    def interpolate_texture(self, x, y, polygon, tex_coords):
        # Barycentric coordinate interpolation
        # Simplified version - just average for this demo
        u = sum(tc[0] for tc in tex_coords) / len(tex_coords)
        v = sum(tc[1] for tc in tex_coords) / len(tex_coords)
        return u, v