from transformer import Transformer

class Window:
    def __init__(self, system, coordinates: list[tuple[float, float, float]]):
        # p0, p1, p2, p3 | p0 -> w_min, p2 -> w_max
        self.coordinates : list[tuple[float, float, float]]
        self.up_vector   : tuple[float, float, float]
        self.right_vector: tuple[float, float, float]
        self.vpn         : tuple[float, float, float]
        self.vrp         : tuple[float, float, float]
        self.cop         : tuple[float, float, float]

        self.system = system
        self.coordinates = coordinates
        self.up_vector = (0, 1, 0)
        self.right_vector = (1, 0, 0)
        self.vpn = (0, 0, 1)
        self.vrp = self.get_center()
        self.cop_dist = 300
        self.cop = (0, 0, self.get_center()[2]-self.cop_dist)


    def get_center(self):
        coordinates = self.coordinates
        coords = [tuple(t) for t in coordinates]
        if (coords[0] == coords[-1]) and (len(coords) > 1):
            coords.pop()

        average_x, average_y, average_z = 0, 0, 0
        for x, y, z in coords:
            average_x += x
            average_y += y
            average_z += z
        points_num = len(coords)
        average_x /= points_num
        average_y /= points_num
        average_z /= points_num

        return (average_x, average_y, average_z)


    def set_coordinates(self, new_coord: list[tuple[float, float, float]]):
        self.coordinates = new_coord


    #axis can be "w_center", "x", "y" and "z"
    def rotate(self, degrees: int, axis: str):
        transformation_list = []
        vec_transformation_list = []
        if (axis in ("x", "y", "z")):
            self.system.transformer.add_rotation(transformation_list, degrees, axis)
            self.system.transformer.add_rotation(vec_transformation_list, degrees, axis)
        else:
            offset_x, offset_y, offset_z = self.get_center()
            self.system.transformer.add_translation(transformation_list, -offset_x, -offset_y, -offset_z)

            self.system.transformer.add_align_matrix(transformation_list, self.system.window.vpn, [0, 1, 0])
            self.system.transformer.add_align_matrix(vec_transformation_list, self.system.window.vpn, [0, 1, 0])

            self.system.transformer.add_rotation(transformation_list, degrees, "y")
            self.system.transformer.add_rotation(vec_transformation_list, degrees, "y")

            self.system.transformer.add_align_matrix(transformation_list, [0, 1, 0], self.system.window.vpn)
            self.system.transformer.add_align_matrix(vec_transformation_list, [0, 1, 0], self.system.window.vpn)

            self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)

        self.up_vector = self.system.transformer.transform([self.up_vector], vec_transformation_list)[0]
        self.right_vector = self.system.transformer.transform([self.right_vector], vec_transformation_list)[0]
        self.vpn = self.system.transformer.transform([self.vpn], vec_transformation_list)[0]
        self.cop = self.system.transformer.transform([self.cop], transformation_list)[0]
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def zoom(self, factor: float):
        transformation_list = []
        self.system.transformer.add_scaling(transformation_list, factor)
        self.cop = self.system.transformer.transform([self.cop], transformation_list)[0]
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def move(self, offset_x: float, offset_y: float, offset_z: float):
        transformation_list = []
        self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)
        self.cop = self.system.transformer.transform([self.cop], transformation_list)[0]
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)

