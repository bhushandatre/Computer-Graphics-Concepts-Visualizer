import numpy as np

class Surface:
    def __init__(self, function, bounds=(-3, 3, -3, 3), color=(0, 255, 0), resolution=20):
        self.function = function
        self.bounds = bounds  # (x_min, x_max, z_min, z_max)
        self.color = color
        self.vertices, self.faces = self._generate_surface(resolution)
    
    def _generate_surface(self, resolution):
        vertices = []
        faces = []
        x_min, x_max, z_min, z_max = self.bounds
        
        # Generate vertices
        for i in range(resolution + 1):
            x = x_min + i * (x_max - x_min) / resolution
            for j in range(resolution + 1):
                z = z_min + j * (z_max - z_min) / resolution
                try:
                    y = self.function(x, z)
                    vertices.append([x, y, z])
                except:
                    vertices.append([x, 0, z])
        
        # Generate faces
        for i in range(resolution):
            for j in range(resolution):
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j + 1
                v4 = (i + 1) * (resolution + 1) + j
                
                faces.append([v1, v2, v3, v4])
        
        return vertices, faces
    
    def get_vertex(self, index):
        return np.array(self.vertices[index])