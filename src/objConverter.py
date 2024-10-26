import os
import string

from objects import Object3D

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
        pass
