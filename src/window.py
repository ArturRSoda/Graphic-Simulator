from transformer import Transformer

class Window:
    def __init__(self, system, coordinates: list[tuple[float, float, float]]):
        # p0, p1, p2, p3 | p0 -> w_min, p2 -> w_max
        self.coordinates : list[tuple[float, float, float]]
        self.up_vector   : tuple[float, float, float]
        self.right_vector: tuple[float, float, float]
        self.vpn         : tuple[float, float, float]
        self.vrp         : tuple[float, float, float]

        self.system = system
        self.coordinates = coordinates
        self.up_vector = (0, 1, 0)
        self.right_vector = (1, 0, 0)
        self.vpn = (0, 0, 1)
        self.vrp = self.get_center()


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
    def rotate(self, transformer: Transformer, degrees: int, axis: str):
        transformation_list = []

        if (axis in ("x", "y", "z")):
            transformer.add_rotation(transformation_list, degrees, axis)
        else:
            offset_x, offset_y, offset_z = self.get_center()
            transformer.add_translation(transformation_list, -offset_x, -offset_y, -offset_z)

            x_angle = self.system.angle_between_vectors((1, 0, 0), self.vpn)
            z_angle = self.system.angle_between_vectors((0, 0, 1), self.vpn)
            transformer.add_rotation(transformation_list, x_angle, "x")
            transformer.add_rotation(transformation_list, z_angle, "z")

            transformer.add_rotation(transformation_list, degrees, "y")

            transformer.add_rotation(transformation_list, -x_angle, "x")
            transformer.add_rotation(transformation_list, -z_angle, "z")

            transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)


        self.up_vector = self.system.normalize_vector(transformer.transform([self.up_vector], transformation_list)[0])
        self.right_vector = self.system.normalize_vector(transformer.transform([self.right_vector], transformation_list)[0])
        self.vpn = self.system.normalize_vector(transformer.transform([self.vpn], transformation_list)[0])
        self.coordinates = transformer.transform(self.coordinates, transformation_list)

    def zoom(self, transformer: Transformer, factor: float):
        transformation_list = []
        transformer.add_scaling(transformation_list, factor)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


    def move(self, transformer: Transformer, offset_x: float, offset_y: float, offset_z: float):
        transformation_list = []
        transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)

