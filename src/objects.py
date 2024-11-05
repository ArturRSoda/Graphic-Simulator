import numpy as np
from tkinter import Tk

from transformer import Transformer

class Object3D:
    def __init__(self, system,
                       name                   : str, 
                       color                  : str,
                       type                   : str,
                       coordinates            : list[tuple[float, float, float]],
                       normalized_coordinates : list[tuple[float, float, float]],
                       edges                  : list[tuple[int, int]]):

        self.system = system
        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates
        self.normalized_coordinates = normalized_coordinates
        self.edges = edges

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


    def move(self, offset_x: float, offset_y: float, offset_z: float):
        transformation_list = []
        self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def scale(self, factor: float):
        transformation_list = []
        self.system.transformer.add_scaling(transformation_list, factor, self.get_center())
        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)


    def rotate(self, degrees: int, axis: str):
        transformation_list = []
        if (axis in ("x", "y", "z")):
            self.system.transformer.add_rotation(transformation_list, degrees, axis)
        else:
            offset_x, offset_y, offset_z = self.get_center()

            self.system.transformer.add_translation(transformation_list, -offset_x, -offset_y, -offset_z)

            self.system.transformer.add_align_matrix(transformation_list, self.system.window.vpn, [0, 1, 0])

            self.system.transformer.add_rotation(transformation_list, degrees, "y")

            self.system.transformer.add_align_matrix(transformation_list, [0, 1, 0], self.system.window.vpn)

            self.system.transformer.add_translation(transformation_list, offset_x, offset_y, offset_z)

        self.coordinates = self.system.transformer.transform(self.coordinates, transformation_list)

    def generate_obj(self, offset):
        types = {
            "point": "p",
            "line": "l",
            "wireframe": "l",
            "polygon": "f",
            "curve": "c"
        }

        mtl = ""
        """
        rgb = tuple(((c//256)/255 for c in Tk().winfo_rgb(self.color)))

        mtl += f"newmtl {self.name}\n"
        mtl += f"Kd {rgb[0]} {rgb[1]} {rgb[2]}\n"
        mtl += "\n"
        """

        vertices = ""
        for point in self.coordinates:
            vertices += f"v {point[0]} {point[1]} {point[2]}\n"

        obj = ""
        obj += f"o {self.name}\n"
        #obj += f"usemtl {self.name}\n"
        obj += f"{types[self.type]} "
        obj += " ".join(str(i+offset+1) for i in range(len(self.coordinates))) + "\n"

        offset += len(self.coordinates)

        print(self.name, obj)
        return mtl, vertices, obj, offset


class Point3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "point", coordinates, normalized_coordinates, [])


class Line3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "line", coordinates, normalized_coordinates, [(0, 1)])


class WireFrame3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], edges: list[tuple[int, int]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "wireframe", coordinates, normalized_coordinates, edges)


class Polygon3D(Object3D):
    def __init__(self, system, name: str, color: str, coordinates: list[tuple[float, float, float]], edges: list[tuple[int, int]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "polygon", coordinates, normalized_coordinates, edges)


class BezierCurve3D(Object3D):
    def __init__(self, system, name: str, color: str, control_matrices: list[list[tuple[float, float, float]]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "curve", [], normalized_coordinates, [])

        self.control_matrices = control_matrices

        #self.continuity(self.control_matrices)
        for i, m in enumerate(self.control_matrices):
            self.generate(i, m)


    def continuity(self, matrices: list[list[tuple[float, float, float]]]):
        for m in matrices: m.sort()
        for i in range(len(matrices)-1):
            matrices[i][-4:] = matrices[i+1][:4]

    def get_GB(self, matrix: list[tuple[float, float, float]]) -> tuple:
        lcp = len(matrix)
        GBx = np.array([[x for (x,_,_) in matrix[i:i+4]] for i in range(0, lcp, 4)])
        GBy = np.array([[y for (_,y,_) in matrix[i:i+4]] for i in range(0, lcp, 4)])
        GBz = np.array([[z for (_,_,z) in matrix[i:i+4]] for i in range(0, lcp, 4)])

        return GBx, GBy, GBz

    def generate(self, mi: int, matrix: list[tuple[float, float, float]], step: int=15):
        Mb = np.array([
            [-1,  3, -3,  1],
            [ 3, -6,  3,  0],
            [-3,  3,  0,  0],
            [ 1,  0,  0,  0]
        ])

        s = np.linspace(0, 1, step)
        t = np.linspace(0, 1, step)

        GBx, GBy, GBz = self.get_GB(matrix)

        for i, ti in enumerate(t):
            tv = np.array([ti**3, ti**2, ti, 1])

            for j, si in enumerate(s):
                sv = np.array([si**3, si**2, si, 1])

                xp = float(sv @ Mb @ GBx @ Mb.T @ tv.T)
                yp = float(sv @ Mb @ GBy @ Mb.T @ tv.T)
                zp = float(sv @ Mb @ GBz @ Mb.T @ tv.T)

                self.coordinates.append((xp, yp, zp))
                if (j < step-1):
                    l = len(self.coordinates)
                    self.edges.append((l-1, l))

            if (i < step-1):
                for t in range(step):
                    l = len(self.coordinates)
                    p1 = mi*step**2 + i*step+t
                    p2 = p1+step
                    self.edges.append((p1, p2))


class BSplineCurve3D(Object3D):
    def __init__(self, system, name: str, color: str, control_matrices: list[list[tuple[float, float, float]]], normalized_coordinates: list[tuple[float, float, float]]):
        super().__init__(system, name, color, "curve", [], normalized_coordinates, [])

        self.ax = [[0, 0, 0, 0], [100, 100, 100, 100], [200, 200, 200, 200], [300, 300, 300, 300]]
        self.ay = [[0, 100, 0, 100], [100, 200, 100, 200], [0, 100, 0, 100], [100, 200, 100, 0]]
        self.az = [[0, 100, 200, 300], [0, 100, 200, 300], [0, 100, 200, 300], [0, 100, 200, 300]]

        self.b = np.array([[-1, 3, -3, 1],
                      [3, -6, 3, 0],
                      [-3, 3, 0, 0],
                      [1, 0, 0, 0]])

        # Initialize matrices
        self.Cx = np.zeros((4, 4))
        self.Cy = np.zeros((4, 4))
        self.Cz = np.zeros((4, 4))

        self.Es = np.zeros((4, 4))
        self.Et = np.zeros((4, 4))

        self.DDx = np.zeros((4, 4))
        self.DDy = np.zeros((4, 4))
        self.DDz = np.zeros((4, 4))

        self.draw_surface_fwd_dif(100, 100)


    def calculate_coefficients(self):
        self.Cx = self.b @ self.ax @ np.transpose(self.b)
        self.Cy = self.b @ self.ay @ np.transpose(self.b)
        self.Cz = self.b @ self.az @ np.transpose(self.b)
        

    def create_delta_matrices(self,delta_s, delta_t):
        self.Es = np.array([[0, 0, 0, 1],
                       [delta_s**3, delta_s**2, delta_s, 0],
                       [6 * delta_s**3, 2 * delta_s**2, 0, 0],
                       [6 * delta_s**3, 0, 0, 0]])

        self.Et = np.array([[0, 0, 0, 1],
                       [delta_t**3, delta_t**2, delta_t, 0],
                       [6 * delta_t**3, 2 * delta_t**2, 0, 0],
                       [6 * delta_t**3, 0, 0, 0]])

        self.Et = np.transpose(self.Et)


    def create_forward_diff_matrices(self):
        self.DDx = self.Es @ self.Cx @ self.Et
        self.DDy = self.Es @ self.Cy @ self.Et
        self.DDz = self.Es @ self.Cz @ self.Et


    def update_forward_diff_matrices(self):
        for i in range(3):
            self.DDx[i] += self.DDx[i+1]
            self.DDy[i] += self.DDy[i+1]
            self.DDz[i] += self.DDz[i+1]


    def draw_curve_fwd_dif(self, n, x, Dx, D2x, D3x, y, Dy, D2y, D3y, z, Dz, D2z, D3z):
        points = []
        for _ in range(n):
            x += Dx; Dx += D2x; D2x += D3x
            y += Dy; Dy += D2y; D2y += D3y
            z += Dz; Dz += D2z; D2z += D3z
            points.append((x, y, z))
        return points


    def draw_surface_fwd_dif(self, ns, nt):
        self.create_delta_matrices(1.0 / (ns - 1), 1.0 / (nt - 1))
        self.create_forward_diff_matrices()

        curves = []
        for _ in range(ns):
            curve = self.draw_curve_fwd_dif(nt, self.DDx[0][0], self.DDx[0][1], self.DDx[0][2], self.DDx[0][3],
                                       self.DDy[0][0], self.DDy[0][1], self.DDy[0][2], self.DDy[0][3],
                                       self.DDz[0][0], self.DDz[0][1], self.DDz[0][2], self.DDz[0][3])
            curves.append(curve)
            self.update_forward_diff_matrices()

        self.coordinates = curves


class Object:
    def __init__(self, name: str, 
                       color: str,
                       type: str,
                       coordinates: list[tuple[float, float]],
                       normalized_coordinates: list[tuple[float, float]]):

        self.name = name
        self.color = color
        self.type = type
        self.coordinates = coordinates
        self.normalized_coordinates = normalized_coordinates

    def get_center(self):
        coordinates = self.coordinates
        coords = [tuple(t) for t in coordinates]
        if (coords[0] == coords[-1]) and (len(coords) > 1):
            coords.pop()

        average_x, average_y = 0, 0
        for x, y in coords:
            average_x += x
            average_y += y
        points_num = len(coords)
        average_x /= points_num
        average_y /= points_num

        return (average_x, average_y)


    def rotate(self, transformer: Transformer, degrees: int, rotation_point: tuple[float, float]):
        transformation_list = []
        transformer.add_rotation(transformation_list, degrees, rotation_point)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


    def scale(self, transformer: Transformer, factor: float):
        transformation_list = []
        transformer.add_scaling(transformation_list, factor, self.get_center())
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


    def move(self, transformer: Transformer, offset_x: float, offset_y: float):
        transformation_list = []
        transformer.add_translation(transformation_list, offset_x, offset_y)
        self.coordinates = transformer.transform(self.coordinates, transformation_list)


class Point(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "point", coordinates, normalized_coordinates)


class Line(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "line", coordinates, normalized_coordinates)


class WireFrame(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "wireframe", coordinates, normalized_coordinates)


class Polygon(Object):
    def __init__(self, name: str, color: str, coordinates: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "polygon", coordinates, normalized_coordinates)


class BezierCurve(Object):
    def __init__(self, name: str, color: str, control_points: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]], n: int=100):
        super().__init__(name, color, "curve", [], normalized_coordinates)

        self.control_points = control_points
        self.step = n
        self.generate()


    def cubic_bezier(self, p0, p1, p2, p3, t):
        return (1 - t)**3 * np.array(p0) + \
               3 * (1 - t)**2 * t * np.array(p1) + \
               3 * (1 - t) * t**2 * np.array(p2) + \
               t**3 * np.array(p3)


    def generate(self):
        t_values = np.linspace(0, 1, self.step)
        cp_num = len(self.control_points)
        for i in range(0, cp_num - 3, 3):
            p0, p1, p2, p3 = self.control_points[i:i+4]

            # g1 continuity
            if i + 4 < cp_num:
                self.control_points[i+4] = 2 * np.array(p3) - np.array(p2)

            segment = [self.cubic_bezier(p0, p1, p2, p3, t) for t in t_values]
            coords = [(float(x), float(y)) for (x, y) in segment]
            self.coordinates.extend(coords)

        # ensures all the points are used
        if cp_num % 3 != 1:
            p0, p1, p2 = self.control_points[-3:]
            p3 = p2
            segment = [self.cubic_bezier(p0, p1, p2, p3, t) for t in t_values]
            coords = [(float(x), float(y)) for (x, y) in segment]
            self.coordinates.extend(coords)


class BSplineCurve(Object):
    def __init__(self, name: str, color: str, control_points: list[tuple[float, float]], normalized_coordinates: list[tuple[float, float]]):
        super().__init__(name, color, "curve", [], normalized_coordinates)

        self.control_points = control_points
        self.delta = 0.01

        self.e_delta = np.array([
            [              0,               0,          0, 1],
            [  self.delta**3,   self.delta**2, self.delta, 0],
            [6*self.delta**3, 2*self.delta**2,          0, 0],
            [6*self.delta**3,               0,          0, 0]
        ])

        self.matriz_bs_base = (1/6) * np.array([
                                          [-1,  3, -3,  1],
                                          [ 3, -6,  3,  0],
                                          [-3,  0,  3,  0],
                                          [ 1,  4,  1,  0]
                                      ])

        self.generate()


    def get_geometry_vector(self, vetor):
        g_x = np.array([x for (x, _) in vetor])
        g_y = np.array([y for (_, y) in vetor])
        return g_x, g_y

    def generate(self):
        n = int(1/self.delta)
        i = 0
        while (i+4 <= len(self.control_points)):
            points = self.control_points[i:i+4]
            i += 1

            g_x, g_y = self.get_geometry_vector(points)
            m_bs = self.matriz_bs_base

            c_x = np.matmul(m_bs, g_x)
            c_y = np.matmul(m_bs, g_y)

            fx, d_fx, d2_fx, d3_fx = np.matmul(self.e_delta, c_x)
            fy, d_fy, d2_fy, d3_fy = np.matmul(self.e_delta, c_y)

            self.fwd_diff(n, fx, d_fx, d2_fx, d3_fx, fy, d_fy, d2_fy, d3_fy)


    def fwd_diff(self, n, x, dx, d2x, d3x, y, dy, d2y, d3y):
        i = 1
        self.coordinates.append((float(x), float(y)))
        while (i < n):
            i += 1
            x, dx, d2x = x+dx, dx+d2x, d2x+d3x
            y, dy, d2y = y+dy, dy+d2y, d2y+d3y
            self.coordinates.append((float(x), float(y)))
