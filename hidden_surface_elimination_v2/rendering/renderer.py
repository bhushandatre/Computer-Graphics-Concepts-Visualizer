import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
from math import atan2, degrees, sqrt

class Renderer:
    def __init__(self, scene, camera):
        self.scene = scene
        self.camera = camera

    def render(self):
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim([-20, 20])
        ax.set_ylim([-20, 20])
        ax.set_zlim([-20, 20])

        # Calculate camera viewing angle
        dx = self.camera.look_at[0] - self.camera.position[0]
        dy = self.camera.look_at[1] - self.camera.position[1]
        dz = self.camera.look_at[2] - self.camera.position[2]

        r = sqrt(dx**2 + dy**2 + dz**2)
        azim = degrees(atan2(dy, dx))
        elev = degrees(atan2(dz, sqrt(dx**2 + dy**2)))
        ax.view_init(elev=elev, azim=azim)

        for obj in self.scene.get_objects():
            pos = obj["position"]
            scale = obj["scale"]
            if obj["type"] == "Cube":
                self.draw_cube(ax, pos, scale)
            elif obj["type"] == "Sphere":
                self.draw_sphere(ax, pos, scale)
            elif obj["type"] == "Pyramid":
                self.draw_pyramid(ax, pos, scale)
            elif obj["type"] == "Cone":
                self.draw_cone(ax, pos, scale)
            elif obj["type"] == "Cylinder":
                self.draw_cylinder(ax, pos, scale)

        return fig

    def draw_cube(self, ax, pos, scale):
        x, y, z = pos
        r = [-1 * scale, 1 * scale]
        vertices = [[x+i, y+j, z+k] for i in r for j in r for k in r]
        faces = [
            [vertices[j] for j in [0,1,3,2]],
            [vertices[j] for j in [4,5,7,6]],
            [vertices[j] for j in [0,1,5,4]],
            [vertices[j] for j in [2,3,7,6]],
            [vertices[j] for j in [0,2,6,4]],
            [vertices[j] for j in [1,3,7,5]]
        ]
        ax.add_collection3d(Poly3DCollection(faces, facecolors='cyan', edgecolors='k', linewidths=1, alpha=0.5))

    def draw_sphere(self, ax, pos, scale):
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x = scale * np.cos(u)*np.sin(v) + pos[0]
        y = scale * np.sin(u)*np.sin(v) + pos[1]
        z = scale * np.cos(v) + pos[2]
        ax.plot_surface(x, y, z, color='orange', alpha=0.6)

    def draw_pyramid(self, ax, pos, scale):
        x, y, z = pos
        s = scale
        base = np.array([[x-s,y-s,z], [x+s,y-s,z], [x+s,y+s,z], [x-s,y+s,z]])
        apex = np.array([x,y,z+2*s])
        faces = [
            [base[0], base[1], apex],
            [base[1], base[2], apex],
            [base[2], base[3], apex],
            [base[3], base[0], apex],
            base
        ]
        ax.add_collection3d(Poly3DCollection(faces, facecolors='purple', edgecolors='k', alpha=0.6))

    def draw_cone(self, ax, pos, scale):
        x, y, z = pos
        h = 2 * scale
        r = 1 * scale
        theta = np.linspace(0, 2*np.pi, 30)
        X = r * np.cos(theta) + x
        Y = r * np.sin(theta) + y
        Z = np.full_like(X, z)
        apex = np.array([x, y, z + h])
        for i in range(len(X)-1):
            verts = [[X[i], Y[i], Z[i]], [X[i+1], Y[i+1], Z[i+1]], apex]
            ax.add_collection3d(Poly3DCollection([verts], color='green', alpha=0.6))

    def draw_cylinder(self, ax, pos, scale):
        x, y, z = pos
        h = 2 * scale
        r = 1 * scale
        z_vals = np.linspace(z, z+h, 10)
        theta = np.linspace(0, 2*np.pi, 30)
        theta_grid, z_grid = np.meshgrid(theta, z_vals)
        X = r * np.cos(theta_grid) + x
        Y = r * np.sin(theta_grid) + y
        Z = z_grid
        ax.plot_surface(X, Y, Z, color='brown', alpha=0.5)
