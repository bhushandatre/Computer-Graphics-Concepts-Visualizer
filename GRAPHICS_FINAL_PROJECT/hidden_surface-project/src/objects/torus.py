import numpy as np

class Torus:
    def __init__(self, position, major_radius, minor_radius, color, segments=32):
        self.position = np.array(position)
        self.major_radius = major_radius
        self.minor_radius = minor_radius
        self.color = color
        self.segments = segments
        self.vertices, self.faces = self.generate_torus()
    
    def generate_torus(self):
        vertices = []
        faces = []
        
        for i in range(self.segments):
            theta = 2 * np.pi * i / self.segments
            for j in range(self.segments):
                phi = 2 * np.pi * j / self.segments
                
                # Torus parametric equations
                x = (self.major_radius + self.minor_radius * np.cos(phi)) * np.cos(theta)
                y = (self.major_radius + self.minor_radius * np.cos(phi)) * np.sin(theta)
                z = self.minor_radius * np.sin(phi)
                
                vertices.append([x, y, z])
                
                # Create faces
                next_i = (i + 1) % self.segments
                next_j = (j + 1) % self.segments
                
                idx = i * self.segments + j
                idx_i = next_i * self.segments + j
                idx_j = i * self.segments + next_j
                idx_ij = next_i * self.segments + next_j
                
                faces.append([idx, idx_i, idx_ij, idx_j])
        
        return vertices, faces
    
    def get_vertex(self, index):
        return self.position + np.array(self.vertices[index])