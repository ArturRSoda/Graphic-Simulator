import tkinter as tk
from tkinter import  messagebox
from tkinter.filedialog import askopenfile, askdirectory
from tkinter import ttk

from objects import Object3D


class Frame(tk.Frame):
    def __init__(self, parent, width: float, height: float):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="groove")


class Label(tk.Label):
    def __init__(self, parent, text: str, size: int):
        super().__init__(parent, text=text, font=("Helvetica", size))


class Tab(ttk.Frame):
    def __init__(self, parent, width: float, height: float):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="ridge")


class CGSystemInterface():
    def __init__(self, system):
        self.menu_frame            : Frame
        self.object_menu_frame     : Frame
        self.controls_menu_frame   : Frame
        self.rotation_menu_frame   : Frame
        self.line_clip_frame       : Frame
        self.canvas_frame          : Frame
        self.messageBox_frame      : Frame
        self.messageBox            : tk.Listbox
        self.objects_listbox       : tk.Listbox
        self.canvas                : tk.Canvas
        self.rotation_opt_var      : tk.StringVar
        self.line_clip_opt_var     : tk.StringVar
        self.window_rotation_opt   : tk.StringVar
        self.window_degrees_var    : tk.DoubleVar
        self.object_degrees_var    : tk.DoubleVar
        self.window_offset_entr    : tk.Entry
        self.obj_offset_entry      : tk.Entry
        self.w_zoom_factor_entry   : tk.Entry
        self.obj_scale_factor_entry: tk.Entry
        self.obj_rotation_coord_var: tuple[tk.IntVar, tk.IntVar]
        self.w_coord_var           : tuple[tk.IntVar, tk.IntVar, tk.IntVar]
        self.canvas_width          : float
        self.canvas_height         : float
        self.subcanvas_height      : float
        self.subcanvas_width       : float
        self.tab_width             : float
        self.tab_height            : float
        self.subcanvas_shift       : float
        self.rotation_Xpoint_entry : tk.Entry
        self.rotation_Ypoint_entry : tk.Entry
        self.obj_center_rb         : tk.Radiobutton
        self.origin_rb             : tk.Radiobutton
        self.other_rb              : tk.Radiobutton
        self.menu_tab              : ttk.Notebook
        self.window_controls_tab   : Tab
        self.obj_controls_tab      : Tab
        self.clipping_tab          : Tab
        self.canvas_elements       : list
        self.menu_bar              : tk.Menu

        self.app = tk.Tk()
        self.app.title("Computer Graphics System")
        self.app.geometry("1000x700")
        self.system = system
        self.canvas_elements = list()

        self.add_menu_bar()
        self.add_menu()
        self.add_canvas()
        self.add_messagesBox()


    def add_menu_bar(self):
        self.menu_bar = tk.Menu(self.app)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Import", command=self.import_file)
        #file_menu.add_command(label="Export", command=self.export_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.app.quit)

        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.app.config(menu=self.menu_bar)


    def import_file(self):
        file = askopenfile(mode='r', filetypes=[("Object Files", "*.obj")])
        if (file is None): return

        self.system.import_obj(file.name)


    def export_file(self):
        dir_path = askdirectory()
        print("dir path: %s" % dir_path)


    def add_canvas(self):
        self.app.update()

        self.canvas_frame = Frame(self.app, self.app.winfo_width()-self.menu_frame.winfo_width()-20, 500)
        self.canvas_frame.place(x=self.menu_frame.winfo_width()+20, y=10)

        Label(self.canvas_frame, "Viewport", 10).place(x=10, y=10)

        self.app.update()
        self.canvas_width = self.canvas_frame.winfo_width()-35
        self.canvas_height = self.canvas_frame.winfo_height()-70
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.place(x=10, y=30)


        self.subcanvas_shift = 20
        self.subcanvas_width = self.canvas_width-(2*self.subcanvas_shift)
        self.subcanvas_height = self.canvas_height-(2*self.subcanvas_shift)

        # gray lines
        shift = self.subcanvas_shift
        l1 = self.canvas.create_line(shift, (self.subcanvas_height/2)+shift,
                                     self.subcanvas_width+shift, (self.subcanvas_height/2)+shift,
                                     fill="gray", width=2)

        l2 = self.canvas.create_line((self.subcanvas_width/2)+shift, shift,
                                     (self.subcanvas_width/2)+shift, self.subcanvas_height+shift,
                                     fill="gray", width=2)

        l3 = self.canvas.create_line(shift, shift,
                                     shift, self.subcanvas_height+shift,
                                     self.subcanvas_width+shift, self.subcanvas_height+shift,
                                     self.subcanvas_width+shift, shift,
                                     shift, shift,
                                     fill="gray", width=2)

        self.canvas_elements.append(l1)
        self.canvas_elements.append(l2)
        self.canvas_elements.append(l3)


    def clear_canvas(self):
        for i in range(3, len(self.canvas_elements)):
            self.canvas.delete(self.canvas_elements[i])


    def draw_object(self, obj: Object3D, obj_vp_coords: list[tuple[float, float]]):
        if (obj.type == "point"):
            coord = obj_vp_coords[0]
            p = self.canvas.create_oval(coord[0], coord[1], coord[0], coord[1], outline=obj.color, width=5)
            self.canvas_elements.append(p)

        elif (obj.type == "polygon"):
            flatten_coords = [c for coord in obj_vp_coords for c in coord]
            plg = self.canvas.create_polygon(flatten_coords, fill=obj.color)
            self.canvas_elements.append(plg)

        elif (obj.type in ("line", "wireframe")):
            for i in range(0, len(obj_vp_coords)-1, 2):
                start_coord = obj_vp_coords[i]
                end_coord = obj_vp_coords[i+1]

                l = self.canvas.create_line(start_coord[0], start_coord[1], end_coord[0], end_coord[1], fill=obj.color, width=2)
                self.canvas_elements.append(l)

        elif (obj.type == "curve"):
            for i in range(len(obj_vp_coords)-1):
                start_coord = obj_vp_coords[i]
                end_coord = obj_vp_coords[i+1]

                l = self.canvas.create_line(start_coord[0], start_coord[1], end_coord[0], end_coord[1], fill=obj.color, width=2)
                self.canvas_elements.append(l)


    def add_menu(self):
        self.app.update()
        self.menu_frame = Frame(self.app, 300, self.app.winfo_height()-20)
        self.menu_frame.place(x=10, y=10)

        self.app.update()
        self.add_object_menu()
        self.add_tab()


    def add_object_menu(self):
        self.object_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 180)
        self.object_menu_frame.place(x=10, y=10)

        Label(self.object_menu_frame, "Objects", 10).place(x=10, y=10)

        self.app.update()
        self.objects_listbox = tk.Listbox(self.object_menu_frame, width=self.object_menu_frame.winfo_width()-247, height=5)
        self.objects_listbox.place(x=10, y=30)

        tk.Button(self.object_menu_frame, text="Add", command=self.system.add_object).place(x=35, y=135)
        tk.Button(self.object_menu_frame, text="Del", command=self.del_object).place(x=90, y=135)
        tk.Button(self.object_menu_frame, text="Transform", command=self.init_transformation_window).place(x=145, y=135)


    def init_transformation_window(self):
        selected = self.objects_listbox.curselection()
        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return
        obj_id = selected[0]
        self.system.init_transformation_window(obj_id)


    def add_tab(self):
        self.app.update()
        self.menu_tab = ttk.Notebook(self.menu_frame)

        self.tab_width = self.menu_frame.winfo_width()-26
        self.tab_height = self.menu_frame.winfo_height()-self.object_menu_frame.winfo_height()-50

        self.add_window_tab_elements()
        self.add_object_tab_elements()
        self.add_clipping_tab()

        self.menu_tab.place(x=10, y=self.object_menu_frame.winfo_height()+15)


    def add_clipping_tab(self):
        self.clipping_tab = Tab(self.menu_tab, width=self.tab_width, height=self.tab_height)

        self.line_clip_frame = Frame(self.clipping_tab, self.tab_width-26, 100)
        self.line_clip_frame.place(x=10, y=10)

        Label(self.line_clip_frame, "Line", 10).place(x=10, y=10)

        self.line_clip_opt_var = tk.StringVar(self.line_clip_frame, "liang_barsky")
        l2 = tk.Radiobutton(self.line_clip_frame, text="Liang Barsky", variable=self.line_clip_opt_var, value="liang_barsky", highlightthickness=0, command=self.line_clip_message)
        l1 = tk.Radiobutton(self.line_clip_frame, text="Cohen Sutherland", variable=self.line_clip_opt_var, value="cohen_sutherland", highlightthickness=0, command=self.line_clip_message)
        l1.place(x=0, y=60)
        l2.place(x=0, y=30)
        self.menu_tab.add(self.clipping_tab, text="Clipping")


    def line_clip_message(self):
        ln_func = self.line_clip_opt_var.get()
        self.add_message("Line clipping function changed to %s" % ln_func)


    def add_window_tab_elements(self):
        self.window_controls_tab = Tab(self.menu_tab, width=self.tab_width, height=self.tab_height)

        self.add_controls_menu(isObject=False)
        self.add_window_rotation_menu()

        self.menu_tab.add(self.window_controls_tab, text="Window")


    def add_object_tab_elements(self):
        self.obj_controls_tab = Tab(self.menu_tab, width=self.tab_width, height=self.tab_height)

        self.add_controls_menu(isObject=True)
        self.add_obj_rotation_menu()

        self.menu_tab.add(self.obj_controls_tab, text="Object")


    def add_controls_menu(self, isObject: bool):
        # if isObject == True then "object controls" else "window controls"

        parent = self.obj_controls_tab if (isObject) else self.window_controls_tab

        self.controls_menu_frame = Frame(parent, self.tab_width-26, 250)
        self.controls_menu_frame.place(x=10, y=10)

        Label(self.controls_menu_frame, "Controls", 10).place(x=10, y=10)

        move_func = self.move_object if (isObject) else self.move_window
        tk.Button(self.controls_menu_frame, text="Up", command=lambda: move_func("up")).place(x=40, y=40)
        tk.Button(self.controls_menu_frame, text="Left", command=lambda: move_func("left")).place(x=10, y=70)
        tk.Button(self.controls_menu_frame, text="Right", command=lambda: move_func("right")).place(x=62, y=70)
        tk.Button(self.controls_menu_frame, text="Down", command=lambda: move_func("down")).place(x=30, y=100)
        tk.Button(self.controls_menu_frame, text="In", command=lambda: move_func("in")).place(x=10, y=130)
        tk.Button(self.controls_menu_frame, text="Out", command=lambda: move_func("out")).place(x=72, y=130)

        scale_func = self.scale_object if (isObject) else self.zoom_window
        tk.Button(self.controls_menu_frame, text="Increase" if (isObject) else "Zoom In", command=lambda: scale_func("in")).place(x=145, y=80)
        tk.Button(self.controls_menu_frame, text="Decrease" if (isObject) else "Zoom Out", command=lambda: scale_func("out")).place(x=145, y=120)

        set_coord_func = self.set_obj_coord if (isObject) else self.set_window_coord
        tk.Button(self.controls_menu_frame, text="Set Coord", command=lambda: self.set_coord_window(set_coord_func)).place(x=80, y=200)

        Label(self.controls_menu_frame, "Offset", 10).place(x=10, y=170)
        Label(self.controls_menu_frame, "Escl. Factor" if (isObject) else "zoom factor", 10).place(x=115, y=170)

        if (isObject):
            self.obj_scale_factor_entry = tk.Entry(self.controls_menu_frame, width=4)
            self.obj_offset_entry = tk.Entry(self.controls_menu_frame, width=4)
            self.obj_offset_entry.insert(0, "10")
            self.obj_scale_factor_entry.insert(0, "2.0")
            self.obj_offset_entry.place(x=55, y=170)
            self.obj_scale_factor_entry.place(x=195, y=170)
        else:
            self.window_offset_entry = tk.Entry(self.controls_menu_frame, width=4)
            self.w_zoom_factor_entry = tk.Entry(self.controls_menu_frame, width=4)
            self.window_offset_entry.insert(0, "10")
            self.w_zoom_factor_entry.insert(0, "2.0")
            self.window_offset_entry.place(x=55, y=170)
            self.w_zoom_factor_entry.place(x=195, y=170)


    def add_window_rotation_menu(self):
        self.rotation_menu_frame = Frame(self.window_controls_tab, self.tab_width-26, 150)
        self.rotation_menu_frame.place(x=10, y=270)

        Label(self.rotation_menu_frame, "Rotation", 10).place(x=10, y=10)

        self.window_rotation_opt = tk.StringVar(self.rotation_menu_frame, "w_center")
        tk.Radiobutton(self.rotation_menu_frame, text="W Center", variable=self.window_rotation_opt, value="w_center").place(x=0, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="X", variable=self.window_rotation_opt, value="x").place(x=90, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="Y", variable=self.window_rotation_opt, value="y").place(x=140, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="Z", variable=self.window_rotation_opt, value="z").place(x=190, y=35)

        self.window_degrees_var = tk.DoubleVar()
        self.window_degrees_var.set(10.)
        Label(self.rotation_menu_frame, "Degrees", 10).place(x=10, y=65)
        tk.Entry(self.rotation_menu_frame, textvariable=self.window_degrees_var, width=4).place(x=70, y=65)

        tk.Button(self.rotation_menu_frame, text="Anti-ClockWise", command=lambda: self.rotate_window(True)).place(x=5, y=100)
        tk.Button(self.rotation_menu_frame, text="ClockWise", command=lambda: self.rotate_window(False)).place(x=145, y=100)


    def add_obj_rotation_menu(self):
        self.rotation_menu_frame = Frame(self.obj_controls_tab, self.tab_width-26,150)
        self.rotation_menu_frame.place(x=10, y=270)

        Label(self.rotation_menu_frame, "Rotation", 10).place(x=10, y=10)

        self.rotation_opt_var = tk.StringVar(self.rotation_menu_frame, "obj_axis")
        tk.Radiobutton(self.rotation_menu_frame, text="Obj axis", variable=self.rotation_opt_var, value="obj_axis").place(x=0, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="X", variable=self.rotation_opt_var, value="x").place(x=90, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="Y", variable=self.rotation_opt_var, value="y").place(x=140, y=35)
        tk.Radiobutton(self.rotation_menu_frame, text="Z", variable=self.rotation_opt_var, value="z").place(x=190, y=35)

        self.object_degrees_var = tk.DoubleVar()
        self.object_degrees_var.set(10.)
        Label(self.rotation_menu_frame, "Degrees", 10).place(x=10, y=65)
        tk.Entry(self.rotation_menu_frame, textvariable=self.object_degrees_var, width=4).place(x=70, y=65)

        tk.Button(self.rotation_menu_frame, text="Anti-ClockWise", command=lambda: self.rotate_object(True)).place(x=5, y=100)
        tk.Button(self.rotation_menu_frame, text="ClockWise", command=lambda: self.rotate_object(False)).place(x=145, y=100)


    def del_object(self):
        tp = self.objects_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delte!")
            return

        id = tp[0]
        self.system.del_object(id)

        self.add_message("Object Deleted")


    def set_coord_window(self, func):
        selected = self.objects_listbox.curselection()
        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return

        obj_id = selected[0]

        app = tk.Toplevel()
        app.title("Set Coordinates")
        app.geometry("250x150")

        Label(app, "Coordinates", 10).place(x=10, y=10)

        fm = Frame(app, width=240, height=50)
        fm.place(x=10, y=30)

        self.w_coord_var = (tk.IntVar(), tk.IntVar(), tk.IntVar())

        Label(fm, "X:", 10).place(x=10, y=15)
        tk.Entry(fm, textvariable=self.w_coord_var[0], width=4).place(x=30, y=10)
        Label(fm, "Y:", 10).place(x=80, y=15)
        tk.Entry(fm, textvariable=self.w_coord_var[1], width=4).place(x=100, y=10)
        Label(fm, "Z:", 10).place(x=150, y=15)
        tk.Entry(fm, textvariable=self.w_coord_var[2], width=4).place(x=170, y=10)

        tk.Button(app, text="Set", command=lambda: func(obj_id)).place(x=60, y=90)
        tk.Button(app, text="Cancel", command=app.destroy).place(x=120, y=90)


    def set_window_coord(self, n):
        coord_x = self.verify_num_entry(self.w_coord_var[0])
        coord_y = self.verify_num_entry(self.w_coord_var[1])
        coord_z = self.verify_num_entry(self.w_coord_var[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            self.system.set_window_coord((coord_x, coord_y, coord_z))
            self.add_message("Window coordinates seted to (%d, %d, %d)" % (coord_x, coord_y, coord_z))


    def set_obj_coord(self, obj_id):
        coord_x = self.verify_num_entry(self.w_coord_var[0])
        coord_y = self.verify_num_entry(self.w_coord_var[1])
        coord_z = self.verify_num_entry(self.w_coord_var[2])

        if (coord_x is not None) and (coord_y is not None) and (coord_z is not None):
            obj = self.system.get_object(obj_id)
            obj_name = obj.name + "-" + obj.type
            self.system.set_obj_coord(obj_id, (coord_x, coord_y, coord_z))
            self.add_message("%s was moved to (%.1f, %.1f, %.1f)" % (obj_name, coord_x, coord_y, coord_z))


    def add_messagesBox(self):
        self.app.update()
        width = self.app.winfo_width()-self.menu_frame.winfo_width()-20
        height = self.app.winfo_height()-self.canvas_frame.winfo_height()-30
        self.messageBox_frame = Frame(self.app, width, height)
        self.messageBox_frame.place(x=self.menu_frame.winfo_width()+20, y=self.canvas_frame.winfo_height()+20)

        self.app.update()
        self.messageBox = tk.Listbox(self.messageBox_frame, width=72, height=8)
        self.messageBox.place(x=10, y=10)


    def rotate_object(self, anticlockwise: bool):
        degrees = self.verify_num_entry(self.object_degrees_var)
        if (degrees == None): return

        selected = self.objects_listbox.curselection()
        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return

        obj_id = selected[0]

        axis = self.rotation_opt_var.get()
        self.system.rotate_object(anticlockwise, degrees, obj_id, axis)
        obj = self.system.get_object(obj_id)
        obj_name = obj.name + "-" + obj.type

        self.add_message("%s rotated %d degrees %s by %s" % (obj_name, degrees, ("anti-clockwise" if (anticlockwise) else "clockwise"), axis))


    def rotate_window(self, anticlockwise: bool):
        degrees = self.verify_num_entry(self.window_degrees_var)
        if (degrees is None): return

        axis = self.window_rotation_opt.get()
        self.system.rotate_window(degrees, anticlockwise, axis)

        self.add_message("Window rotated %d degrees %s by %s" % (degrees, ("anti-clockwise" if (anticlockwise) else "clockwise"), axis))


    def rotation(self, isObject: bool, antiClockwise: bool):
        # if isObject == True then move object else move window

        degrees = self.verify_num_entry(self.object_degrees_var) if (object) else self.verify_num_entry(self.window_degrees_var)
        if (degrees is None):
            return

        if (not isObject):
            self.system.rotate(False, antiClockwise, degrees, None, None, None)
            return

        selected = self.objects_listbox.curselection()
        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return

        rotation_opt = self.rotation_opt_var.get()
        obj_id = selected[0]

        if (rotation_opt == "Other"):
            coord_x = self.verify_num_entry(self.obj_rotation_coord_var[0])
            coord_y = self.verify_num_entry(self.obj_rotation_coord_var[1])

            if (coord_x is None) or (coord_y is None):
                return

        else:
            coord_x = 0
            coord_y = 0

        self.system.rotate(True, antiClockwise, degrees, obj_id, rotation_opt, (coord_x, coord_y))


    def move_object(self, direction: str):
        offset = self.verify_num_entry(self.obj_offset_entry)
        if (offset is None): return
        selected = self.objects_listbox.curselection()

        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return

        obj_id = selected[0]
        self.system.move_object(offset, direction, obj_id)
        obj = self.system.get_object(obj_id)
        obj_name = obj.name + "-" + obj.type
        self.add_message("%s moved %s by %d" % (obj_name, direction, offset))


    def move_window(self, direction: str):
        offset = self.verify_num_entry(self.window_offset_entry)
        if (offset is None): return
        self.system.move_window(offset, direction)
        self.add_message("window moved %s by %d" % (direction, offset))


    def scale_object(self, inORout: str):
        factor = self.verify_num_entry(self.obj_scale_factor_entry)
        if (factor is None): return
        selected = self.objects_listbox.curselection()
        if (not selected):
            self.send_error("Object not selected", "Please select an object!")
            return

        obj_id = selected[0]
        self.system.scale_object(factor, obj_id, inORout)
        obj = self.system.get_object(obj_id)
        obj_name = obj.name + "-" + obj.type
        self.add_message("%s scaled %s by %.2f" % (obj_name, inORout, factor))


    def zoom_window(self, inORout: str):
        factor = self.verify_num_entry(self.w_zoom_factor_entry)
        if (factor is None): return
        self.system.zoom_window(factor, inORout)
        self.add_message("window zoomed %s by %.2f" % (inORout, factor))


    def verify_num_entry(self, entry) -> int|float|None:
        try:
            value = float(entry.get())
        except Exception:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value


    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)


    def add_message(self, message: str):
        self.messageBox.insert(0, message)

