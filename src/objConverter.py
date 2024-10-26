import os
import string

from objects import *

class ObjConverter():
    def __init__(self, system):
        self.system = system

    def export_obj(self, path: string):
        mtls = ""
        vertices = ""
        objs = ""
        offset = 0

        objects = self.system.display_file
        for obj in objects:
            m, v, o, offset = obj.generate_obj(offset)
            mtls += m
            vertices += v
            objs += o

        obj_path = f"{path}.obj"
        #mtl_path = f"{path}.mtl"

        with open(obj_path, 'w') as obj_file:
            obj_file.write(vertices)
            #obj_file.write("mtllib " + os.path.basename(mtl_path) + "\n")
            obj_file.write(objs)

        """
        with open(mtl_path, 'w') as mtl_file:
            mtl_file.write(mtls)
        """
    
    def import_obj(self, path: string):
        path_mtl = f"{path}.mtl"
        path_obj = f"{path}.obj"

        vertices = []
        with open(path_obj, 'r') as obj_file:
            for line in obj_file:
                element = line.strip().split()

                if element and element[0] == 'v':
                    vertices.append([float(element[1]), float(element[2]), float(element[3])])

        objects = {}
        with open(path_obj, 'r') as obj_file:
            for line in obj_file:
                element = line.strip().split()
                if not element:
                    continue

                if element[0] == 'o':
                    name = f"{element[1:]}"
                    objects[name] = {'vertices': [], 'type': None, "mtl": ""}

                if element[0] == 'usemtl':
                    objects[name]["mtl"] = name

                if element[0] in ("l", "f", "p",  "c"):
                    objects[name]["type"] = element[0]
                    objects[name]["vertices"] = [int(v)-1 for v in element[1:]]

        mtl = {}
        with open(path_mtl, 'r') as mtl_file:
            for line in mtl_file:
                element = line.strip().split()
                if not element:
                    continue

                if element[0] == 'newmtl':
                    name = " ".join(element[1:])
                    mtl[name] = {}

                if element[0] == 'Kd':
                    mtl[name]["color"] = [float(c) for c in element[1:]]

        new_objects = []
        for obj, attr in objects.items():
            name = obj
            points = [vertices[v] for v in attr["vertices"]]
            print(points)
            color = "black"

            if len(points) == 1:
                self.system.add_point(name, color, points[0])
            elif len(points) == 2:
                self.system.add_line(name, color, points[0], points[1])
            elif len(points) > 2:
                if attr["type"] == "f":
                    self.system.add_wireframe(name, color, points, [])
                elif attr["type"] == "c":
                    self.system.add_curve(name, color, points)
                else:
                    self.system.add_wireframe(name, color, points, [])
