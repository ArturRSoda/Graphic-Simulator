import os

from objects import *

class ObjConverter():
    def __init__(self, system):
        self.system = system

    def export_obj(self, path: str):
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
        mtl_path = f"{path}.mtl"

        with open(obj_path, 'w') as obj_file:
            obj_file.write(vertices)
            obj_file.write("mtllib " + os.path.basename(mtl_path) + "\n")
            obj_file.write(objs)


    def verify_name(self, name: str) -> bool:
        if (name == ""):
            self.system.interface.send_error("Read Error", "Poorly structured obj file.\n Remeber the name of the object: 'o {name}'")
            return False
        return True

    def import_obj(self, path: str):
        path_mtl = f"{path}.mtl"
        path_obj = f"{path}.obj"

        vertices = []
        with open(path_obj, 'r') as obj_file:
            for line in obj_file:
                element = line.strip().split()

                if (element) and (element[0] == 'v'):
                    vertices.append([float(element[1]), float(element[2]), float(element[3])])

        objects = {}
        with open(path_obj, 'r') as obj_file:
            name = ""
            for line in obj_file:
                element = line.strip().split()
                if (not element): continue

                if (element[0] == 'o'):
                    name = f"{element[1:]}"
                    objects[name] = {'vertices': set(), 'faces': [], 'type': None, "mtl": ""}

                elif (element[0] == 'usemtl'):
                    objects[name]["mtl"] = element[1]

                elif (element[0] in ("l", "f", "p", "c")):
                    if (not self.verify_name(name)): return
                    objects[name]["type"] = element[0]
                    objects[name]["vertices"].update([int(v)-1 for v in element[1:]])

                    if (element[0] == "f"):
                        objects[name]["faces"].append([int(v)-1 for v in element[1:]])

        mtl = {}
        try:
            mtl_file = open(path_mtl, 'r')
        except:
            pass
        else:
            for line in mtl_file:
                element = line.strip().split()
                if (not element): continue

                if (element[0] == 'newmtl'):
                    name = " ".join(element[1:])
                    mtl[name] = {}

                if (element[0] == 'Kd'):
                    mtl[name]["color"] = "#%02x%02x%02x" % tuple([int(float(c)*255) for c in element[1:]])

        for obj, attr in objects.items():
            name = obj
            points = [vertices[v] for v in attr["vertices"]]
            color = mtl[objects[name]['mtl']]['color'] if (objects[name]['mtl']) else "black"

            edges = set()
            for face in attr["faces"]:
                num_vertices = len(face)
                for i in range(num_vertices - 1):
                    v1 = face[i]
                    v2 = face[i + 1]
                    edges.add((min(v1, v2), max(v1, v2)))

                if face[0] == face[-1]:
                    v1 = face[-1]
                    v2 = face[0]
                    edges.add((min(v1, v2), max(v1, v2)))
            edges = list(edges)

            edges_ = list()
            for (a, b) in edges:
                va, vb = vertices[a], vertices[b]
                ia, ib = points.index(va), points.index(vb)
                edges_.append((ia, ib))

            if len(points) == 1:
                self.system.add_point(name, color, points[0])
            elif len(points) == 2:
                self.system.add_line(name, color, points[0], points[1])
            elif len(points) > 2:
                if attr["type"] == "f":
                    self.system.add_wireframe(name, color, points, edges_)
                elif attr["type"] == "c":
                    self.system.add_curve(name, color, points)
                else:
                    self.system.add_wireframe(name, color, points, edges_)
