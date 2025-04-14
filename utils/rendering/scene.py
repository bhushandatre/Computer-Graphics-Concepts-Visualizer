class Scene:
    def __init__(self):
        self.objects = []

    def add_object(self, object_type, position=(0, 0, 0), scale=1.0):
        self.objects.append({"type": object_type, "position": position, "scale": scale})

    def get_objects(self):
        return self.objects
