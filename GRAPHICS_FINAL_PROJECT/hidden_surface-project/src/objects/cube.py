import numpy as np

class Cube:
    def __init__(self, position=(0, 0, 5), size=1, color=(255, 0, 0)):
        self.position = np.array(position)
        self.size = size
        self.color = color
        self.vertices = self._generate_vertices()
        self.faces = self._generate_faces()
    
    def _generate_vertices(self):
        hs = self.size / 2  # half size
        return [
            [-hs, -hs, -hs], [hs, -hs, -hs], [hs, hs, -hs], [-hs, hs, -hs],
            [-hs, -hs, hs], [hs, -hs, hs], [hs, hs, hs], [-hs, hs, hs]
        ]
    
    def _generate_faces(self):
        return [
            [0, 1, 2, 3],  # back face
            [4, 5, 6, 7],  # front face
            [0, 1, 5, 4],  # bottom face
            [2, 3, 7, 6],  # top face
            [0, 3, 7, 4],  # left face
            [1, 2, 6, 5]   # right face
        ]
    
    def get_vertex(self, index):
        return self.position + np.array(self.vertices[index])