W_MAX = 1
W_MIN = -1

# FUNCTIONS AND VARIABLES FOR COHEN-SUTHERLAND LINE CLIPPING
LEFT = 1    # 0001
RIGHT = 2   # 0010
BOTTOM = 4  # 0100
TOP = 8     # 1000

def get_region_code(coord: tuple[float, float]) -> int:
    code = 0

    x = coord[0]
    y = coord[1]

    if (y > 1):
        code |= TOP
    elif (y < -1):
        code |= BOTTOM

    if (x < -1):
        code |= LEFT
    elif (x > 1):
        code |= RIGHT

    return code

def calculate_intersection_point(coord1: tuple[float, float], coord2: tuple[float, float], intersections, id):
    x1, y1 = coord1
    x2, y2 = coord2

    m = (y2 - y1) / (x2 - x1) if (x2 - x1) else 0
    x = y = 0
    if ("top" in intersections):
            x = (x1 + (1/m) * (W_MAX - y1)) if (m) else x1
            y = W_MAX
            if (id == 1):
                x1, y1 = x, y
            else:
                x2, y2 = x, y

    if ("bottom" in intersections):
            x = (x1 + (1/m) * (W_MIN - y1)) if (m) else x1
            y = W_MIN
            if (id == 1):
                x1, y1 = x, y
            else:
                x2, y2 = x, y

    if ("left" in intersections):
            x = W_MIN
            y = y1 + m * (W_MIN - x1)
            if (id == 1):
                x1, y1 = x, y
            else:
                x2, y2 = x, y

    if ("right" in intersections):
            x = W_MAX
            y = y1 + m * (W_MAX - x1)
            if (id == 1):
                x1, y1 = x, y
            else:
                x2, y2 = x, y

    return (x1, y1) if (id == 1) else (x2, y2)


def detect_intersection(code):
    intersections = list()
    if (code & TOP):
        intersections.append("top")
    if (code & BOTTOM):
        intersections.append("bottom")
    if (code & LEFT):
        intersections.append("left")
    if (code & RIGHT):
        intersections.append("right")
    return intersections


def cohen_sutherland(line: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
    coord1 = line[0]
    coord2 = line[1]

    code1 = get_region_code(coord1)
    code2 = get_region_code(coord2)

    if (code1 & code2) != 0: # line is parallel and outside the window, so reject
        return None

    if (code1 | code2) == 0: # line is completely inside the window, so dont need clipping
        return line

    intersections = detect_intersection(code1)
    if (intersections):
        coord1  = calculate_intersection_point(coord1, coord2, intersections, 1)

    x, y = coord1
    if (x < -1) or (x > 1) or (y < -1) or (y > 1): # if some coords is outside the boundary, after the calculation of intersections
        return None                                # than the line dont pass through the window, so reject

    intersections = detect_intersection(code2)
    if (intersections):
        coord2  = calculate_intersection_point(coord1, coord2, intersections, 2)

    return [coord1, coord2]


# FUNCTION LIANG-BARSKY LINE CLIPPING
def liang_barsky(line: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
    x1, y1 = line[0]
    x2, y2 = line[1]

    dx = x2 - x1
    dy = y2 - y1

    p = [-dx, dx, -dy, dy]
    q = [x1-W_MIN, W_MAX-x1, y1-W_MIN, W_MAX-y1]

    # if (pi == 0) and (qi == 0) then
    #   line is parallel and outside the window, so reject
    if ( (p[0] == 0 and q[0] < 0) or
         (p[1] == 0 and q[1] < 0) or
         (p[2] == 0 and q[2] < 0) or
         (p[3] == 0 and q[3] < 0) ):
        return None

    u1 = max([0] + [q[i]/p[i] for i in range(4) if p[i] < 0])
    u2 = min([1] + [q[i]/p[i] for i in range(4) if p[i] > 0])

    # if (u1 > u2) then
    #   line is completely outside the window, so reject
    if (u1 > u2):
        return None

    # clipping coordinates
    new_x1 = x1 + u1*dx
    new_y1 = y1 + u1*dy
    new_x2 = x1 + u2*dx
    new_y2 = y1 + u2*dy

    return [(new_x1, new_y1), (new_x2, new_y2)]


