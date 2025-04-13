import numpy as np
import pygame
from utils.math_utils import project_point

class FloatingHorizon:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.reset_horizons()
    
    def reset_horizons(self):
        self.upper_horizon = np.full(self.width, -np.inf)
        self.lower_horizon = np.full(self.width, np.inf)
    
    def render(self, screen, objects, camera_pos, camera_angle):
        self.reset_horizons()
        screen.fill((0, 0, 0))
        
        # Find surface objects
        surfaces = [obj for obj in objects if hasattr(obj, 'function')]
        
        if not surfaces:
            return
        
        surface = surfaces[0]  # Just use the first surface
        
        # Sample the surface in z-order (back to front)
        z_min, z_max = surface.bounds[2], surface.bounds[3]
        z_step = (z_max - z_min) / 100
        
        for z in np.arange(z_max, z_min, -z_step):
            # Sample curve at this z
            x_min, x_max = surface.bounds[0], surface.bounds[1]
            x_step = (x_max - x_min) / 100
            prev_point = None
            
            for x in np.arange(x_min, x_max, x_step):
                try:
                    y = surface.function(x, z)
                    point = np.array([x, y, z])
                    
                    # Project to 2D
                    px, py = project_point(point, camera_pos, camera_angle, self.width, self.height)
                    
                    if px < 0 or px >= self.width:
                        continue
                    
                    # Check against horizons
                    px_int = int(px)
                    
                    if py > self.upper_horizon[px_int]:
                        pygame.draw.line(screen, (255, 0, 0), (px_int, py), (px_int, self.upper_horizon[px_int]))
                        self.upper_horizon[px_int] = py
                    
                    if py < self.lower_horizon[px_int]:
                        pygame.draw.line(screen, (0, 0, 255), (px_int, py), (px_int, self.lower_horizon[px_int]))
                        self.lower_horizon[px_int] = py
                    
                    if prev_point is not None:
                        prev_px, prev_py = prev_point
                        pygame.draw.line(screen, (255, 255, 255), (prev_px, prev_py), (px, py), 1)
                    
                    prev_point = (px, py)
                except:
                    prev_point = None
                    continue