import numpy as np
import math as m

class Transformator:
    def __init__(self, system):
        self.system = system

    def add_translation(self, transformation_list: list[list[list]], offset_x: float, offset_y: float):
        transformation_list.insert(1, np.array([[1, 0, 0],
                                                [0, 1, 0],
                                                [offset_x, offset_y, 1]]))


    def add_scaling(self, transformation_list: list[list[list]], scale_factor: float, transformation_point: tuple[float, float]=(0, 0)):
        if transformation_point != (0, 0):
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [-transformation_point[0], -transformation_point[1], 1]]))
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [transformation_point[0], transformation_point[1], 1]]))

        transformation_list.insert(1, np.array([[scale_factor, 0, 0],
                                                [0, scale_factor, 0],
                                                [0, 0, 1]]))


    def add_rotation(self, transformation_list: list[list[list]], rotation_degrees: float, transformation_point: tuple[float, float]=(0, 0)):
        if transformation_point != (0, 0):
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [-transformation_point[0], -transformation_point[1], 1]]))
            transformation_list.append(np.array([[1, 0, 0],
                                                 [0, 1, 0],
                                                 [transformation_point[0], transformation_point[1], 1]]))

        s = m.sin(m.radians(rotation_degrees))
        c = m.cos(m.radians(rotation_degrees))
        transformation_list.insert(1, np.array([[c, s, 0],
                                                [-s, c, 0],
                                                [0, 0, 1]]))

    def transform(self, coordinates: list[tuple[float, float]], transformation_list: list[list[list]]):
        transformation_matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        for matrix in transformation_list:
            transformation_matrix = np.matmul(transformation_matrix, matrix)

        new_coordinates = []
        for i in range(len(coordinates)):
            x = coordinates[i][0]
            y = coordinates[i][1]
            coord_matrix = np.array([x, y, 1])
            new_coord_matrix = np.matmul(coord_matrix, transformation_matrix)
            new_coordinates.append((new_coord_matrix[0].item(), new_coord_matrix[1].item()))

        return new_coordinates


    # transformation_typle_list = [ tranformation_type : str,
    #                               factor             : float,
    #                               rotation_center    : (float, float) | None
    #                               antiClockwise      : bool | None ]
    # tranformation can be: "move_up", "move_down", "move_left", "move_right",
    #                       "increase_scale", "decrease_scale",
    #                       "rotate_origin", "rotate_obj_center", "rotate_other"
    def apply_transformations(self, obj_coordinates: list[tuple[float, float]], transformation_tuple_list: list[tuple[str, float, tuple[float, float]|None, bool|None]]):
        transformation_list = []

        for transformation_type, factor, rotation_center, antiClockwise in transformation_tuple_list:
            if (antiClockwise is not None) and (not antiClockwise):
                factor = -factor

            match transformation_type:
                case "move_up":
                    self.add_translation(transformation_list, self.system.up_vector[0]*factor,
                                                              self.system.up_vector[1]*factor)
                case "move_down":
                    self.add_translation(transformation_list, -self.system.up_vector[0]*factor,
                                                              -self.system.up_vector[1]*factor)
                case "move_left":
                    self.add_translation(transformation_list, -self.system.right_vector[0]*factor,
                                                              -self.system.right_vector[1]*factor)
                case "move_right":
                    self.add_translation(transformation_list, self.system.right_vector[0]*factor,
                                                              self.system.right_vector[1]*factor)
                case "increase_scale":
                    self.add_scaling(transformation_list, factor, self.system.get_center(obj_coordinates))
                case "decrease_scale":
                    self.add_scaling(transformation_list, 1/factor, self.system.get_center(obj_coordinates))
                case "rotate_origin":
                    self.add_rotation(transformation_list, factor)
                case "rotate_obj_center":
                    self.add_rotation(transformation_list, factor, self.system.get_center(obj_coordinates))
                case "rotate_other":
                    self.add_rotation(transformation_list, factor, rotation_center)

        return self.transform(obj_coordinates, transformation_list)
