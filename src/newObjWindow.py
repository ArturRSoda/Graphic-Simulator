import tkinter as tk
from tkinter import Button, ttk, messagebox

from numpy import ma

from CGSystemInterface import Label, Frame, Tab

class NewObjWindow:
    def __init__(self, system):
        self.tab_menu                : ttk.Notebook
        self.point_tab               : Tab
        self.line_tab                : Tab
        self.wireframe_tab           : Tab
        self.bezier_tab              : Tab
        self.bspline_tab             : Tab
        self.color_opt_frame         : Frame
        self.wireframe_coord_list    : list[tuple[float, float, float]]
        self.bezier_coord_list       : list[list[tuple[float, float, float]]]
        self.bspline_coord_list      : list[list[tuple[float, float, float]]]
        self.bspline_entry_list      : list[tk.Entry]
        self.wireframe_coord_listbox : tk.Listbox
        self.bspline_coord_listbox   : tk.Listbox
        self.color_opt_var           : tk.StringVar
        self.obj_name_var            : tk.StringVar
        self.tab_width               : float
        self.tab_height              : float
        self.bspline_matrix_size     : tk.IntVar

        self.point_coord_tuple       : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.line_start_coord_tuple  : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.line_end_coord_tuple    : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.wireframe_coord_tuple   : tuple[tk.IntVar, tk.IntVar, tk.IntVar]

        self.system = system
        self.app = tk.Toplevel()
        self.app.title("New Object")
        self.app.geometry("400x400")

        self.add_name_obj_entry()
        self.add_color_buttons()
        self.add_tabs()


    def add_name_obj_entry(self):
        Label(self.app, "Name:", 10).place(x=10, y=15)

        self.obj_name_var = tk.StringVar()
        tk.Entry(self.app, textvariable=self.obj_name_var, width=35).place(x=60, y=10)


    def add_color_buttons(self):
        self.app.update()
        self.color_opt_frame = Frame(self.app, self.app.winfo_width()-20, 60)
        self.color_opt_frame.place(x=10, y=40)

        Label(self.color_opt_frame, "Color:", 10).place(x=10, y=10)

        self.color_opt_var = tk.StringVar(self.color_opt_frame, "Red")
        tk.Radiobutton(self.color_opt_frame, text="Red", variable=self.color_opt_var, value="Red").place(x=10, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Blue", variable=self.color_opt_var, value="Blue").place(x=70, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Green", variable=self.color_opt_var, value="Green").place(x=130, y=30)
        tk.Radiobutton(self.color_opt_frame, text="Black", variable=self.color_opt_var, value="Black").place(x=200, y=30)


    def add_tabs(self):
        self.tab_menu = ttk.Notebook(self.app)

        self.tab_width = self.app.winfo_width()-20
        self.tab_height = self.app.winfo_height()-self.color_opt_frame.winfo_height()-135

        self.add_point_tab()
        self.add_line_tab()
        self.add_wireframe_tab()
        self.add_bezier_tab()
        self.add_bspline_tab()

        self.tab_menu.place(x=10, y=105)


    def add_coord_frame(self, parent, x: float, y: float, variables: tuple[tk.IntVar, tk.IntVar, tk.IntVar]):
        fm = Frame(parent, width=240, height=50)
        fm.place(x=x, y=y)

        Label(fm, "X:", 10).place(x=10, y=10)
        tk.Entry(fm, textvariable=variables[0], width=4).place(x=30, y=10)

        Label(fm, "Y:", 10).place(x=80, y=10)
        tk.Entry(fm, textvariable=variables[1], width=4).place(x=100, y=10)

        Label(fm, "Z:", 10).place(x=150, y=10)
        tk.Entry(fm, textvariable=variables[2], width=4).place(x=170, y=10)


    def add_point_tab(self):
        self.point_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.point_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        ttk.Label(self.point_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.point_tab, 10, 30, self.point_coord_tuple)

        tk.Button(self.point_tab, text="Add", command=self.add_point).place(x=80, y=self.tab_height-45)
        tk.Button(self.point_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.point_tab, text="Point")


    def add_line_tab(self):
        self.line_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        ttk.Label(self.line_tab, text="Start Coordinates").place(x=10, y=10)
        ttk.Label(self.line_tab, text="End Coordinates").place(x=10, y=90)

        self.line_start_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())
        self.line_end_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        self.add_coord_frame(self.line_tab, 10, 30, self.line_start_coord_tuple)
        self.add_coord_frame(self.line_tab, 10, 110, self.line_end_coord_tuple)

        tk.Button(self.line_tab, text="Add", command=self.add_line).place(x=80, y=self.tab_height-45)
        tk.Button(self.line_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.line_tab, text="Line")


    def add_wireframe_tab(self):
        self.wireframe_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.wireframe_coord_list = list()
        self.wireframe_coord_tuple = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        ttk.Label(self.wireframe_tab, text="Coordinates").place(x=10, y=10)
        self.add_coord_frame(self.wireframe_tab, 10, 30, self.wireframe_coord_tuple)

        ttk.Label(self.wireframe_tab, text="Added Coordinates").place(x=250, y=10)
        self.wireframe_coord_listbox = tk.Listbox(self.wireframe_tab, width=10, height=7)
        self.wireframe_coord_listbox.place(x=260, y=30)

        tk.Button(self.wireframe_tab, text="Add Coord", command=self.add_wireframe_coord).place(x=10, y=90)
        tk.Button(self.wireframe_tab, text="Del Coord", command=self.del_wireframe_coord).place(x=10, y=130)
        tk.Button(self.wireframe_tab, text="Add", command=self.add_wireframe).place(x=80, y=self.tab_height-45)
        tk.Button(self.wireframe_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.wireframe_tab, text="WireFrame")


    def add_bezier_tab(self):
        self.bezier_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.bezier_coord_list = list()

        tk.Button(self.bezier_tab, text="Add Matrix", command=self.add_bezier_matrix).place(x=10, y=40)

        Label(self.bezier_tab, "Added Matrices", 10).place(x=130, y=10)
        self.bezier_coord_listbox = tk.Listbox(self.bezier_tab, width=25, height=9)
        self.bezier_coord_listbox.place(x=130, y=40)

        tk.Button(self.bezier_tab, text="Add", command=lambda: self.add_surface("bezier")).place(x=80, y=self.tab_height-45)
        tk.Button(self.bezier_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.bezier_tab, text="Bezier")


    def add_bspline_tab(self):
        self.bspline_tab = Tab(self.tab_menu, width=self.tab_width, height=self.tab_height)

        self.bspline_coord_list = list()

        tk.Button(self.bspline_tab, text="Add Matrix", command=self.add_bspline_matrix).place(x=10, y=40)

        Label(self.bspline_tab, "Matrix size: ", 10).place(x=20, y=70)
        self.bspline_matrix_size = tk.IntVar(self.bspline_tab, 4)
        tk.Entry(self.bspline_tab, textvariable=self.bspline_matrix_size, width=4).place(x=35, y=90)

        Label(self.bspline_tab, "Added Matrices", 10).place(x=130, y=10)
        self.bspline_coord_listbox = tk.Listbox(self.bspline_tab, width=25, height=9)
        self.bspline_coord_listbox.place(x=130, y=40)

        tk.Button(self.bspline_tab, text="Add", command=lambda: self.add_surface("bspline")).place(x=80, y=self.tab_height-45)
        tk.Button(self.bspline_tab, text="Cancel", command=self.cancel).place(x=210, y=self.tab_height-45)

        self.tab_menu.add(self.bspline_tab, text="BSpline")


    def add_wireframe_coord(self):
        coord_x = self.verify_num_entry(self.wireframe_coord_tuple[0])
        coord_y = self.verify_num_entry(self.wireframe_coord_tuple[1])
        coord_z = self.verify_num_entry(self.wireframe_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            self.wireframe_coord_list.append((coord_x, coord_y, coord_z))
            self.wireframe_coord_listbox.insert(tk.END, "(%d, %d, %d)" % (coord_x, coord_y, coord_z))


    def del_wireframe_coord(self):
        tp = self.wireframe_coord_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delete!")
            return

        id = tp[0]
        self.wireframe_coord_listbox.delete(id)
        self.wireframe_coord_list.pop(id)


    def add_bspline_matrix(self):
        if (self.bspline_coord_list):
            self.send_error("Matrix already added", "Its only possible add one matrix")
            return

        matrix_size = self.verify_num_entry(self.bspline_matrix_size)
        if (matrix_size is None): return

        if (matrix_size > 10) or (matrix_size < 4):
            self.send_error("Invalid Matrix Size", "Matrix size must be between 4 and 10")

        matrix_size = int(matrix_size)

        app_width = 180 + 110*(matrix_size-1)
        app_height = 80 + 20*(matrix_size-1)

        app = tk.Toplevel()
        app.title("Add Bezier Matrix")
        app.geometry("%dx%d" % (app_width, app_height))

        Label(app, "Ctrl. Points", 10).grid(row=0, column=0)
        c_acc = 1
        for _ in range(matrix_size-1):
            Label(app, "X", 10).grid(row=0, column=c_acc)
            Label(app, "Y", 10).grid(row=0, column=c_acc+1)
            Label(app, "Z", 10).grid(row=0, column=c_acc+2)
            Label(app, "|", 10).grid(row=0, column=c_acc+3)
            c_acc += 4
        Label(app, "X", 10).grid(row=0, column=c_acc); Label(app, "Y", 10).grid(row=0, column=c_acc+1); Label(app, "Z", 10).grid(row=0, column=c_acc+2)

        entries: list[tuple[tk.Entry, tk.Entry, tk.Entry]] = list()
        for i in range(1, matrix_size+1):
            Label(app, "%d" % i, 10).grid(row=i, column=0)

            c_acc = 1
            for _ in range(matrix_size):
                ex, ey, ez = tk.Entry(app, width=4), tk.Entry(app, width=4), tk.Entry(app, width=4)
                ex.grid(row=i, column=c_acc); ey.grid(row=i, column=c_acc+1); ez.grid(row=i, column=c_acc+2)
                entries.append((ex, ey, ez))
                c_acc += 4

        cs = int((4*matrix_size+1)/2)
        tk.Button(app, text="Add", command=lambda: self.add_coord_matrix(app, entries, "bspline")).grid(row=matrix_size+1, column=0, columnspan=8)
        tk.Button(app, text="Cancel", command=app.destroy).grid(row=matrix_size+1, column=cs, columnspan=cs)

    def add_bezier_matrix(self):
        app = tk.Toplevel()
        app.title("Add Bezier Matrix")
        app.geometry("600x150")

        Label(app, "Ctrl. Points", 10).grid(row=0, column=0)
        Label(app, "X1", 10).grid(row=0, column=1); Label(app, "Y1", 10).grid(row=0, column=2); Label(app, "Z1", 10).grid(row=0, column=3)
        Label(app, "|", 10).grid(row=0, column=4)
        Label(app, "Y2", 10).grid(row=0, column=6); Label(app, "X2", 10).grid(row=0, column=5); Label(app, "Z2", 10).grid(row=0, column=7)
        Label(app, "|", 10).grid(row=0, column=8)
        Label(app, "X3", 10).grid(row=0, column=9); Label(app, "Y3", 10).grid(row=0, column=10); Label(app, "Z3", 10).grid(row=0, column=11)
        Label(app, "|", 10).grid(row=0, column=12)
        Label(app, "X4", 10).grid(row=0, column=13); Label(app, "Y4", 10).grid(row=0, column=14); Label(app, "Z4", 10).grid(row=0, column=15)

        entries: list[tuple[tk.Entry, tk.Entry, tk.Entry]] = list()
        for i in range(1, 5):
            ex1, ey1, ez1 = tk.Entry(app, width=4), tk.Entry(app, width=4), tk.Entry(app, width=4)
            ex2, ey2, ez2 = tk.Entry(app, width=4), tk.Entry(app, width=4), tk.Entry(app, width=4)
            ex3, ey3, ez3 = tk.Entry(app, width=4), tk.Entry(app, width=4), tk.Entry(app, width=4)
            ex4, ey4, ez4 = tk.Entry(app, width=4), tk.Entry(app, width=4), tk.Entry(app, width=4)
            entries.extend([(ex1, ey1, ez1), (ex2, ey2, ez2), (ex3, ey3, ez3), (ex4, ey4, ez4)])

            Label(app, "%d" % i, 10).grid(row=i, column=0)
            ex1.grid(row=i, column=1); ey1.grid(row=i, column=2); ez1.grid(row=i, column=3)
            ex2.grid(row=i, column=5); ey2.grid(row=i, column=6); ez2.grid(row=i, column=7)
            ex3.grid(row=i, column=9); ey3.grid(row=i, column=10); ez3.grid(row=i, column=11)
            ex4.grid(row=i, column=13); ey4.grid(row=i, column=14); ez4.grid(row=i, column=15)

        tk.Button(app, text="Add", command=lambda: self.add_coord_matrix(app, entries, "bezier")).grid(row=17, column=0, columnspan=8)
        tk.Button(app, text="Cancel", command=app.destroy).grid(row=17, column=8, columnspan=8)


    def add_coord_matrix(self, app, entries: list[tuple[tk.Entry, tk.Entry, tk.Entry]], surface_str: str):
        matrix = list()
        for (ex, ey, ez) in entries:
            x = self.verify_num_entry(ex)
            if (x is None): break
            y = self.verify_num_entry(ey)
            if (y is None): break
            z = self.verify_num_entry(ez)
            if (z is None): break

            matrix.append((x, y, z))
        else:
            if (surface_str == "bezier"):
                if (not self.verify_continuity(matrix)):
                    self.send_error("Must have continuity", "Some side of the new matrix must be the same as some matrix already added, for continuity")
                    return

                self.bezier_coord_list.append(matrix)
                coord_listbox = self.bezier_coord_listbox
            else:
                self.bspline_coord_list.append(matrix)
                coord_listbox = self.bspline_coord_listbox

            step = int(len(matrix)**(1/2))
            for i in range(0, step):
                message = "   "
                for j in range(step):
                    message += "(%d, %d, %d)" % matrix[i*step+j]
                coord_listbox.insert(0, message)

            coord_listbox.insert(0, "%d ->" % len(self.bezier_coord_list) if (surface_str == "bezier") else len(self.bspline_coord_list))
            app.destroy()


    def get_matrix_sides(self, matrix: list[tuple[float, float, float]]) -> list[list[tuple[float, float, float]]]:
        top = matrix[:4]
        bottom = matrix[-4:]
        left = matrix[0:13:4]
        right = matrix[3:16:4]
        return [top, bottom, left, right]


    def verify_continuity(self, matrix: list[tuple[float, float, float]]) -> bool:
        if (not self.bezier_coord_list): return True

        matrix_top, matrix_bottom, matrix_left, matrix_right = self.get_matrix_sides(matrix)
        for added_m in self.bezier_coord_list:
            for side in self.get_matrix_sides(added_m):
                if (side == matrix_top): return True
                if (side == matrix_bottom): return True
                if (side == matrix_left): return True
                if (side == matrix_right): return True

        return False


    def add_point(self):
        coord_x = self.verify_num_entry(self.point_coord_tuple[0])
        coord_y = self.verify_num_entry(self.point_coord_tuple[1])
        coord_z = self.verify_num_entry(self.point_coord_tuple[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            name = self.obj_name_var.get()
            color = self.color_opt_var.get()
            self.system.add_point(name, color, (coord_x, coord_y, coord_z))

            self.system.interface.add_message("    - Coord:  (%d, %d, %d)" % (coord_x, coord_y, coord_z))
            self.system.interface.add_message("    - Color:  %s" % color)
            self.system.interface.add_message("    - Name:  %s" % name)
            self.system.interface.add_message("Point added:")

            self.app.destroy()


    def add_line(self):
        start_coord_x = self.verify_num_entry(self.line_start_coord_tuple[0])
        start_coord_y = self.verify_num_entry(self.line_start_coord_tuple[1])
        start_coord_z = self.verify_num_entry(self.line_start_coord_tuple[2])

        end_coord_x = self.verify_num_entry(self.line_end_coord_tuple[0])
        end_coord_y = self.verify_num_entry(self.line_end_coord_tuple[1])
        end_coord_z = self.verify_num_entry(self.line_end_coord_tuple[2])

        if (start_coord_x is not None) and (start_coord_y is not None) and (start_coord_z is not None) and (end_coord_x is not None) and (end_coord_y is not None) and (end_coord_z is not None):
            start_coord = (start_coord_x, start_coord_y, start_coord_z)
            end_coord = (end_coord_x, end_coord_y, end_coord_z)
            name = self.obj_name_var.get()
            color = self.color_opt_var.get()

            self.system.add_line(name, color, start_coord, end_coord)

            self.system.interface.add_message("    - Coord:  (%d, %d, %d) to (%d, %d, %d)" % (start_coord[0], start_coord[1], start_coord[2], end_coord[0], end_coord[1], end_coord[2]))
            self.system.interface.add_message("    - Color:  %s" % color)
            self.system.interface.add_message("    - Name:  %s" % name)
            self.system.interface.add_message("Line added:")

            self.app.destroy()


    def add_wireframe(self):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        if (len(self.wireframe_coord_list) < 2):
            self.send_error("More coordinates", "Please informe at least 2 coordinates!")
            return

        edges = list()
        for i in range(len(self.wireframe_coord_list)-1):
            edges.append((i, i+1))

        self.system.add_wireframe(name, color, self.wireframe_coord_list, edges)

        coords = ""
        edges_str = ""
        for (c1, c2) in edges: edges_str += "(%d, %d)" % (c1, c2)
        for v in self.wireframe_coord_list: coords += "(%d, %d, %d) " % v
        self.system.interface.add_message("    - Edges: %s" % edges_str)
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("Wireframe added:")

        self.app.destroy()


    def add_surface(self, surface_str: str):
        name = self.obj_name_var.get()
        color = self.color_opt_var.get()

        coord_list = self.bezier_coord_list if (surface_str == "bezier") else self.bspline_coord_list

        if (not coord_list):
            self.send_error("Empty list of matrices", "At least one control coordinate matrix must be passed")
            return

        self.system.add_surface(name, color, coord_list, surface_str)

        coords = ""
        for m in self.bezier_coord_list:
            for c in m:
                coords += "(%d, %d, %d) " % c
        self.system.interface.add_message("    - Coord:  %s" % coords)
        self.system.interface.add_message("    - Color:  %s" % color)
        self.system.interface.add_message("    - Name:  %s" % name)
        self.system.interface.add_message("%s surface added:" % surface_str)

        self.app.destroy()


    def cancel(self):
        self.app.destroy()


    def verify_num_entry(self, entry) -> int|float|None:
        try:
            value = float(entry.get())
        except Exception as e:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value


    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)

