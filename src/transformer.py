import numpy as np
from math import cos, sin, radians

class Transformer:
    def __init__(self, system):
        self.system = system

    def add_translation(self, transformation_list: list[list[list]], offset_x: float, offset_y: float, offset_z: float):
        transformation_list.append(np.array(
            [[ 1, 0, 0, offset_x],
             [ 0, 1, 0, offset_y],
             [ 0, 0, 1, offset_z],
             [ 0, 0, 0,        1]]
        ))


    def add_scaling(self, transformation_list: list[list[list]], scale_factor: float, transformation_point: tuple[float, float, float]=(0, 0, 0)):
        m = np.array(
            [[scale_factor,            0,            0, 0],
             [           0, scale_factor,            0, 0],
             [           0,            0, scale_factor, 0],
             [           0,            0,            0, 1]]
        )

        if (transformation_point == (0, 0, 0)):
            transformation_list.append(m)
        else:
            offset_x, offset_y, offset_z = transformation_point
            mt = np.array(
                [[ 1, 0, 0, -offset_x],
                 [ 0, 1, 0, -offset_y],
                 [ 0, 0, 1, -offset_z],
                 [ 0, 0, 0,         1]]
            )
            mtr = np.array(
                [[ 1, 0, 0, offset_x],
                 [ 0, 1, 0, offset_y],
                 [ 0, 0, 1, offset_z],
                 [ 0, 0, 0,        1]]
            )
            transformation_list.append(mt)
            transformation_list.append(m)
            transformation_list.append(mtr)


    def add_rotation(self, transformation_list: list[list[list]], rotation_degrees: float, axis: str, transformation_point: tuple[float, float, float]=(0, 0, 0)):
        s = sin(radians(rotation_degrees))
        c = cos(radians(rotation_degrees))

        if (axis == "x"):
            m = np.array([
                [ 1,  0,  0,  0],
                [ 0,  c, -s,  0],
                [ 0,  s,  c,  0],
                [ 0,  0,  0,  1]
            ])
        elif (axis == "y"):
            m = np.array([
                [ c,  0,  s,  0],
                [ 0,  1,  0,  0],
                [-s,  0,  c,  0],
                [ 0,  0,  0,  1]
            ])
        elif (axis == "z"):
            m = np.array([
                [  c, -s, 0, 0],
                [  s,  c, 0, 0],
                [  0,  0, 1, 0],
                [  0,  0, 0, 1]
            ])

        if (transformation_point == (0, 0, 0)):
            transformation_list.append(m)
        else:
            offset_x, offset_y, offset_z = transformation_point
            mt = np.array(
                [[ 1, 0, 0, -offset_x],
                 [ 0, 1, 0, -offset_y],
                 [ 0, 0, 1, -offset_z],
                 [ 0, 0, 0,         1]]
            )
            mtr = np.array(
                [[ 1, 0, 0, offset_x],
                 [ 0, 1, 0, offset_y],
                 [ 0, 0, 1, offset_z],
                 [ 0, 0, 0,        1]]
            )
            transformation_list.append(mt)
            transformation_list.append(m)
            transformation_list.append(mtr)

    def transform(self, coordinates: list[tuple[float, float, float]], transformation_list: list[list[list]]):
        transformation_matrix = np.eye(4)
        for matrix in reversed(transformation_list):
            transformation_matrix = transformation_matrix @ matrix

        coords = np.array([[*coord, 1] for coord in coordinates])

        new_coords = coords @ transformation_matrix.T
        new_coordinates = [tuple(new_coord[:-1].tolist()) for new_coord in new_coords]

        return new_coordinates


    # transformation_typle_list = [ tranformation_type : str,
    #                               factor             : float,
    #                               rotation_axis      : str | None
    #                               antiClockwise      : bool | None ]
    # tranformation can be: "move_up", "move_down", "move_left", "move_right", "move_out", "move_in"
    #                       "increase_scale", "decrease_scale",
    #                       "rotate"
    # rotation_axis can be: "obj_axis", "x", "y", "z"
    #
    def apply_transformations(self, obj_coordinates: list[tuple[float, float, float]], transformation_tuple_list: list[tuple[str, float, str|None, bool|None]], obj_center: tuple[float, float, float]):
        transformation_list = []

        for transformation_type, factor, axis, antiClockwise in transformation_tuple_list:
            if (antiClockwise is not None) and (not antiClockwise):
                factor = -factor

            match transformation_type:
                case "move_up":
                    self.add_translation(transformation_list, self.system.window.up_vector[0]*factor,
                                                              self.system.window.up_vector[1]*factor,
                                                              self.system.window.up_vector[2]*factor)
                case "move_down":
                    self.add_translation(transformation_list, -self.system.window.up_vector[0]*factor,
                                                              -self.system.window.up_vector[1]*factor,
                                                              -self.system.window.up_vector[2]*factor)
                case "move_left":
                    self.add_translation(transformation_list, -self.system.window.right_vector[0]*factor,
                                                              -self.system.window.right_vector[1]*factor,
                                                              -self.system.window.right_vector[2]*factor)
                case "move_right":
                    self.add_translation(transformation_list, self.system.window.right_vector[0]*factor,
                                                              self.system.window.right_vector[1]*factor,
                                                              self.system.window.right_vector[2]*factor)
                case "move_in":
                    self.add_translation(transformation_list, self.system.window.vpn[0]*factor,
                                                              self.system.window.vpn[1]*factor,
                                                              self.system.window.vpn[2]*factor)
                case "move_out":
                    self.add_translation(transformation_list, -self.system.window.vpn[0]*factor,
                                                              -self.system.window.vpn[1]*factor,
                                                              -self.system.window.vpn[2]*factor)
                case "increase_scale":
                    self.add_scaling(transformation_list, factor, obj_center)

                case "decrease_scale":
                    self.add_scaling(transformation_list, 1/factor, obj_center)

                case "rotate":
                    self.add_rotation(transformation_list, factor, axis)

        return self.transform(obj_coordinates, transformation_list)


    def add_align_matrix(self, transformation_list: list[list[list]], v1: tuple[float, float, float], v2: tuple[float, float, float]):
        v1 = np.array(v1)
        v2 = np.array(v2)

        # Normalize the vectors
        v1_norm = v1 / np.linalg.norm(v1)
        v2_norm = v2 / np.linalg.norm(v2)

        # Calculate the axis of rotation
        rotation_axis = np.cross(v1_norm, v2_norm)

        # If the vectors are parallel, return identity matrix
        if np.linalg.norm(rotation_axis) < 1e-6:
            transformation_list.append(np.eye(4))
            return

        # Calculate the angle of rotation
        cos_theta = np.dot(v1_norm, v2_norm)
        angle = np.arccos(np.clip(cos_theta, -1.0, 1.0))

        # Normalize the rotation axis
        rotation_axis /= np.linalg.norm(rotation_axis)

        # Create the rotation matrix using Rodrigues' formula
        K = np.array([[0, -rotation_axis[2], rotation_axis[1]],
                    [rotation_axis[2], 0, -rotation_axis[0]],
                    [-rotation_axis[1], rotation_axis[0], 0]])
        
        R = np.eye(3) + K * np.sin(angle) + K @ K * (1 - cos_theta)

        # Create a 4x4 rotation matrix
        rotation_matrix_4x4 = np.eye(4)
        rotation_matrix_4x4[:3, :3] = R

        transformation_list.append(np.array(rotation_matrix_4x4))

