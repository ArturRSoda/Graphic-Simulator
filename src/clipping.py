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


def cohen_sutherland(line: list[tuple[float, float]]) -> list[tuple[float, float]]|None:
    x1, y1 = line[0]
    x2, y2 = line[1]

    code1 = get_region_code((x1, y1))
    code2 = get_region_code((x2, y2))

    flag = False
    while True:
        # Line is completely inside the window, so accept
        if (not code1) and (not code2): 
            flag = True
            break

        # Line is parallel and outside the window, so reject
        elif (code1 & code2): 
            break

        else:
            x, y = 1, 1

            # At least one of the point is outside the window, choose one
            code_out = code1 if (code1 != 0) else code2

            # Find and calculate intersection point
            m = (y2 - y1) / (x2 - x1)
            if (code_out & TOP):
                x = x1 + (1/m) * (W_MAX - y1)
                y = W_MAX

            elif (code_out & BOTTOM):
                x = x1 + (1/m) * (W_MIN - y1)
                y = W_MIN

            elif (code_out & RIGHT):
                y = y1 + m * (W_MAX - x1)
                x = W_MAX

            elif (code_out & LEFT):
                y = y1 + m * (W_MIN - x1)
                x = W_MIN


            # Replace the outside point by the calculated intersection point
            if (code_out == code1): 
                x1, y1 = x, y
                code1 = get_region_code((x1, y1))

            else:
                x2, y2 = x, y
                code2 = get_region_code((x2, y2)) 
  
    return [(x1, y1), (x2, y2)] if (flag) else None

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


