from PIL import Image
import numpy as np

class Texture:
    def __init__(self, image_path):
        self.image = Image.open(image_path)
        self.data = np.array(self.image)
    
    @classmethod
    def default(cls):
        # Create a default checkerboard texture
        size = 256
        checker = np.zeros((size, size, 3), dtype=np.uint8)
        tile_size = size // 8
        for i in range(size):
            for j in range(size):
                if (i // tile_size + j // tile_size) % 2 == 0:
                    checker[i, j] = [255, 255, 255]  # White
                else:
                    checker[i, j] = [0, 0, 255]  # Blue
        return cls.from_array(checker)
    
    @classmethod
    def from_array(cls, array):
        tex = cls.__new__(cls)
        tex.data = array
        return tex
    
    def sample(self, u, v):
        """Sample texture with bilinear filtering"""
        u = max(0, min(1, u))
        v = max(0, min(1, v))
        
        height, width = self.data.shape[:2]
        x = u * (width - 1)
        y = v * (height - 1)
        
        x0, y0 = int(x), int(y)
        x1, y1 = min(x0 + 1, width - 1), min(y0 + 1, height - 1)
        
        # Bilinear interpolation
        x_frac, y_frac = x - x0, y - y0
        top = self.data[y0, x0] * (1 - x_frac) + self.data[y0, x1] * x_frac
        bottom = self.data[y1, x0] * (1 - x_frac) + self.data[y1, x1] * x_frac
        return top * (1 - y_frac) + bottom * y_frac