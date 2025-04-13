import numpy as np

class PhongLighting:
    def __init__(self, light_position, ambient=0.2, diffuse=0.7, specular=0.5, shininess=32):
        self.light_position = np.array(light_position)
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
    
    def apply(self, color, normal, view_vector):
        """Apply Phong lighting model to a color"""
        normal = normal / np.linalg.norm(normal)
        view_vector = view_vector / np.linalg.norm(view_vector)
        light_vector = (self.light_position - view_vector)
        light_vector = light_vector / np.linalg.norm(light_vector)
        
        # Ambient
        ambient_component = np.array(color) * self.ambient
        
        # Diffuse
        diffuse_intensity = max(0, np.dot(normal, light_vector))
        diffuse_component = np.array(color) * self.diffuse * diffuse_intensity
        
        # Specular
        reflect_vector = 2 * np.dot(normal, light_vector) * normal - light_vector
        specular_intensity = max(0, np.dot(view_vector, reflect_vector)) ** self.shininess
        specular_component = np.array([255, 255, 255]) * self.specular * specular_intensity
        
        # Combine components
        result = ambient_component + diffuse_component + specular_component
        return np.clip(result, 0, 255).astype(int)