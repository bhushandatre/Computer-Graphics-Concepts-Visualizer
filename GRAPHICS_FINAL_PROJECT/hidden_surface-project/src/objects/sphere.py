import numpy as np

class Sphere:
    def __init__(self, position=(0, 0, 5), radius=1, color=(0, 0, 255), resolution=20):
        self.position = np.array(position)
        self.radius = radius
        self.color = color
        self.vertices, self.faces = self._generate_sphere(resolution)
    
    def _generate_sphere(self, resolution):
        vertices = []
        faces = []
        
        # Generate vertices
        for i in range(resolution + 1):
            theta = i * np.pi / resolution
            for j in range(resolution + 1):
                phi = j * 2 * np.pi / resolution
                x = self.radius * np.sin(theta) * np.cos(phi)
                y = self.radius * np.sin(theta) * np.sin(phi)
                z = self.radius * np.cos(theta)
                vertices.append([x, y, z])
        
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
        return self.position + np.array(self.vertices[index])