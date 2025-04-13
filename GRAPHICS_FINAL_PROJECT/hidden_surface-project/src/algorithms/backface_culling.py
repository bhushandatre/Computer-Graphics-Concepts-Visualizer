import numpy as np
from src.utils.math_utils import calculate_normal, is_backface
from src.utils.rendering import project_point, render_polygon, create_image

class BackfaceCulling:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
    
    def render(self, objects, camera_pos, camera_angle=0):
        image = create_image(self.width, self.height)
        draw = ImageDraw.Draw(image)
        
        for obj in objects:
            for face in obj.faces:
                vertices = [obj.get_vertex(i) for i in face]
                normal = calculate_normal(vertices)
                
                if not is_backface(vertices[0], normal, camera_pos):
                    projected = []
                    for vertex in vertices:
                        point = project_point(vertex, camera_pos, camera_angle, 
                                           self.width, self.height)
                        if point:
                            projected.append(point)
                    
                    if len(projected) >= 3:
                        render_polygon(draw, projected, obj.color)
        
        return image