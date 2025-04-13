import numpy as np
from .zbuffer import ZBuffer
from src.utils import octree

class HierarchicalZBuffer(ZBuffer):
    def __init__(self, width, height, tile_size=16):
        super().__init__(width, height)
        self.tile_size = tile_size
        self.tiles_x = (width + tile_size - 1) // tile_size
        self.tiles_y = (height + tile_size - 1) // tile_size
        self.tile_z = np.full((self.tiles_x, self.tiles_y), np.inf)
    
    def reset_buffers(self):
        super().reset_buffers()
        self.tile_z.fill(np.inf)
    
    def process_face(self, vertices, color, camera_pos, camera_angle, lighting=None):
        # First check against tile Z-buffer
        bbox = self.calculate_bounding_box(vertices, camera_pos, camera_angle)
        
        # Check if any part of the face is potentially visible
        if not self.is_potentially_visible(bbox):
            return
        
        # Process with standard Z-buffer for the affected tiles
        super().process_face(vertices, color, camera_pos, camera_angle, lighting)
    
    def calculate_bounding_box(self, vertices, camera_pos, camera_angle):
        # Project all vertices and find min/max
        min_x, max_x = np.inf, -np.inf
        min_y, max_y = np.inf, -np.inf
        min_z, max_z = np.inf, -np.inf
        
        for vertex in vertices:
            x = vertex[0] * np.cos(camera_angle) - vertex[2] * np.sin(camera_angle)
            z = vertex[0] * np.sin(camera_angle) + vertex[2] * np.cos(camera_angle)
            y = vertex[1]
            
            if z - camera_pos[2] <= 0:
                continue
                
            scale = 500 / (z - camera_pos[2])
            px = self.width // 2 + int(x * scale)
            py = self.height // 2 - int(y * scale)
            
            min_x = min(min_x, px)
            max_x = max(max_x, px)
            min_y = min(min_y, py)
            max_y = max(max_y, py)
            min_z = min(min_z, z)
            max_z = max(max_z, z)
        
        return (max(0, min_x), min(self.width-1, max_x),
                max(0, min_y), min(self.height-1, max_y),
                min_z, max_z)
    
    def is_potentially_visible(self, bbox):
        min_x, max_x, min_y, max_y, min_z, _ = bbox
        
        # Convert to tile coordinates
        tile_min_x = min_x // self.tile_size
        tile_max_x = max_x // self.tile_size
        tile_min_y = min_y // self.tile_size
        tile_max_y = max_y // self.tile_size
        
        # Check all overlapping tiles
        for tx in range(tile_min_x, tile_max_x + 1):
            for ty in range(tile_min_y, tile_max_y + 1):
                if tx < self.tiles_x and ty < self.tiles_y:
                    if min_z < self.tile_z[tx, ty]:
                        self.tile_z[tx, ty] = min_z
                        return True
        return False