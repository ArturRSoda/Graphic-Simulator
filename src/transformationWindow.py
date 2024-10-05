import tkinter as tk
from tkinter import messagebox

from objects import Object
from CGSystemInterface import Label, Frame

class TransformationWindow:
    def __init__(self, system, obj: Object):
        self.obj                        : Object
        self.transformation_list_frame  : Frame
        self.controls_frame             : Frame
        self.translation_controls_frame : Frame
        self.scale_controls_frame       : Frame
        self.rotation_controls_frame    : Frame
        self.offset_entry               : tk.Entry
        self.scale_factor_entry         : tk.Entry
        self.degrees_entry              : tk.Entry
        self.rotation_Xpoint_entry      : tk.Entry
        self.rotation_Ypoint_entry      : tk.Entry
        self.rotation_opt_var           : tk.StringVar
        self.obj_center_rb              : tk.Radiobutton
        self.origin_rb                  : tk.Radiobutton
        self.other_rb                   : tk.Radiobutton
        self.transformation_listbox     : tk.Listbox
        self.transformation_list        : list[tuple[str, float, tuple[float, float] | None, bool | None]]

        self.app = tk.Tk()
        self.app.title("Transformation Window")
        self.app.geometry("650x500")

        self.transformation_list = list()
        self.system = system
        self.obj = obj

        self.add_header()
        self.add_controls()
        self.add_transformation_list()
        self.app.update()


    def add_header(self):
        obj_name = self.obj.name + " - " + self.obj.type
        coord_str = ""
        for c in self.obj.coordinates:
            a, b = [float(x) for x in c]
            coord_str += "(%.1f, %.1f)" % (a, b)

        Label(self.app, "SELECTED OBJECT: %s" % obj_name, 10).place(x=10, y=10)
        Label(self.app, "CURRENT COORDINATES: %s" % coord_str, 10).place(x=10, y=30)

    def add_controls(self):
        self.controls_frame = Frame(self.app, 305, 450)
        self.controls_frame.place(x=10, y=50)

        Label(self.controls_frame, "Controls", 10).place(x=10, y=10)

        self.app.update()
        self.add_translation_controls()
        self.add_scale_controls()
        self.add_rotation_controls()

    def add_translation_controls(self):
        self.translation_controls_frame = Frame(self.controls_frame, 135, 180)
        self.translation_controls_frame.place(x=10, y=30)

        Label(self.translation_controls_frame, "Translation", 10).place(x=10, y=10)

        tk.Button(self.translation_controls_frame, text="Up", command=self.move_up).place(x=40, y=40)
        tk.Button(self.translation_controls_frame, text="Left", command=self.move_left).place(x=10, y=70)
        tk.Button(self.translation_controls_frame, text="Right", command=self.move_right).place(x=62, y=70)
        tk.Button(self.translation_controls_frame, text="Down", command=self.move_down).place(x=30, y=100)

        Label(self.translation_controls_frame, "Offset", 10).place(x=10, y=140)
        self.offset_entry = tk.Entry(self.translation_controls_frame, width=4)
        self.offset_entry.place(x=55, y=140)
        self.offset_entry.insert("end", "10")

    def add_scale_controls(self):
        self.scale_controls_frame = Frame(self.controls_frame, 135, 180)
        self.scale_controls_frame.place(x=155, y=30)

        Label(self.scale_controls_frame, "Escale", 10).place(x=10, y=10)

        tk.Button(self.scale_controls_frame, text="Increase", command=self.increase_scale).place(x=10, y=50)
        tk.Button(self.scale_controls_frame, text="Decrease", command=self.decrease_scale).place(x=10, y=90)

        Label(self.scale_controls_frame, "Escal. Factor", 10).place(x=10, y=140)
        self.scale_factor_entry = tk.Entry(self.scale_controls_frame, width=4)
        self.scale_factor_entry.place(x=90, y=140)
        self.scale_factor_entry.insert("end", "2.0")

    def add_rotation_controls(self):
        width = self.controls_frame.winfo_width()-26
        self.rotation_controls_frame = Frame(self.controls_frame, width, 150)
        self.rotation_controls_frame.place(x=10, y=220)

        Label(self.rotation_controls_frame, "Rotation", 10).place(x=10, y=10)

        Label(self.rotation_controls_frame, "Degrees", 10).place(x=10, y=35)
        self.degrees_entry = tk.Entry(self.rotation_controls_frame, width=4)
        self.degrees_entry.place(x=60, y=35)
        self.degrees_entry.insert("end", "10")

        Label(self.rotation_controls_frame, "X:", 10).place(x=100, y=35)
        Label(self.rotation_controls_frame, "Y:", 10).place(x=170, y=35)
        self.rotation_Xpoint_entry = tk.Entry(self.rotation_controls_frame, state="disabled", width=4)
        self.rotation_Ypoint_entry = tk.Entry(self.rotation_controls_frame, state="disabled", width=4)
        self.rotation_Xpoint_entry.place(x=120, y=35)
        self.rotation_Ypoint_entry.place(x=190, y=35)
        self.rotation_Xpoint_entry.insert("end", "0")
        self.rotation_Ypoint_entry.insert("end", "0")

        self.rotation_opt_var = tk.StringVar(self.rotation_controls_frame, "Origin")
        self.obj_center_rb = tk.Radiobutton(self.rotation_controls_frame, text="Obj Center", variable=self.rotation_opt_var, value="Obj Center", command=self.rotation_point_entry_state)
        self.origin_rb = tk.Radiobutton(self.rotation_controls_frame, text="Origin", variable=self.rotation_opt_var, value="Origin", command=self.rotation_point_entry_state)
        self.other_rb = tk.Radiobutton(self.rotation_controls_frame, text="Other", variable=self.rotation_opt_var, value="Other", command=self.rotation_point_entry_state)
        self.obj_center_rb.place(x=20, y=65)
        self.origin_rb.place(x=100, y=65)
        self.other_rb.place(x=160, y=65)

        tk.Button(self.rotation_controls_frame, text="Anti-ClockWise", command=lambda: self.rotate(True)).place(x=10, y=100)
        tk.Button(self.rotation_controls_frame, text="ClockWise", command=lambda: self.rotate(False)).place(x=150, y=100)

    def rotation_point_entry_state(self):
        if (self.rotation_opt_var.get() == "Other"):
            self.rotation_Xpoint_entry.config(state="normal")
            self.rotation_Ypoint_entry.config(state="normal")
        else:
            self.rotation_Xpoint_entry.config(state="disabled")
            self.rotation_Ypoint_entry.config(state="disabled")


    def add_transformation_list(self):
        self.transformation_list_frame = Frame(self.app, 305, 450)
        self.transformation_list_frame.place(x=325, y=50)

        Label(self.transformation_list_frame, "Transformation List", 10).place(x=10, y=10)

        self.transformation_listbox = tk.Listbox(self.transformation_list_frame, width=30, height=19)
        self.transformation_listbox.place(x=10, y=30)

        tk.Button(self.transformation_list_frame, text="Delete", command=self.del_transformation).place(x=30, y=390)
        tk.Button(self.transformation_list_frame, text="Apply", command=self.apply).place(x=120, y=390)
        tk.Button(self.transformation_list_frame, text="Cancel", command=self.app.destroy).place(x=200, y=390)

    def del_transformation(self):
        selected = self.transformation_listbox.curselection()
        if (not selected):
            self.send_error("Tranformation Not Selected", "Please select a transformation to delete!")
            return

        self.transformation_listbox.delete(selected[0])

    def apply(self):
        self.system.apply_transformations(self.obj, self.transformation_list)

        coord = ""
        for c in self.obj.coordinates:
            coord += "(%.1f, %.1f) " % c
        self.system.interface.add_message("    - " + coord)
        self.system.interface.add_message(self.obj.name + " - " + self.obj.type + " was transformed. New coordinates: ")
        self.app.destroy()

    def move_up(self):
        v = self.verify_num_entry(self.offset_entry)
        if (not v): return

        self.transformation_list.append(("move_up", v, None, None))
        self.transformation_listbox.insert("end", "Move up by %.1f" % v)

    def move_down(self):
        v = self.verify_num_entry(self.offset_entry)
        if (not v): return

        self.transformation_list.append(("move_down", v, None, None))
        self.transformation_listbox.insert("end", "Move down by %.1f" % v)

    def move_left(self):
        v = self.verify_num_entry(self.offset_entry)
        if (not v): return

        self.transformation_list.append(("move_left", v, None, None))
        self.transformation_listbox.insert("end", "Move left by %.1f" % v)

    def move_right(self):
        v = self.verify_num_entry(self.offset_entry)
        if (not v): return

        self.transformation_list.append(("move_right", v, None, None))
        self.transformation_listbox.insert("end", "Move right by %.1f" % v)

    def increase_scale(self):
        v = self.verify_num_entry(self.scale_factor_entry)
        if (not v): return

        self.transformation_list.append(("increase_scale", v, None, None))
        self.transformation_listbox.insert("end", "Increase scale by %.1f" % v)

    def decrease_scale(self):
        v = self.verify_num_entry(self.scale_factor_entry)
        if (not v): return

        self.transformation_list.append(("decrease_scale", v, None, None))
        self.transformation_listbox.insert("end", "Decrease scale by %.1f" % v)

    def rotate(self, antiClockwise: bool):
        v = self.verify_num_entry(self.degrees_entry)
        if (not v): return

        message: str
        t: tuple[str, float, tuple[float, float], bool]
        if (self.rotation_opt_var.get() == "Origin"):
            t = ("rotate_origin", v, (0, 0), antiClockwise)
            message = "Rotated %d degrees by the Origin %s" % (v, ("anti-clockwise" if (antiClockwise) else "clockwise"))
        elif(self.rotation_opt_var.get() == "Obj Center"):
            t = ("rotate_obj_center", v, (0, 0), antiClockwise)
            message = "Rotated %d degrees by the Object Center %s" % (v, ("anti-clockwise" if (antiClockwise) else "clockwise"))
        else:
            x = self.verify_num_entry(self.rotation_Xpoint_entry)
            if (not x): return
            y = self.verify_num_entry(self.rotation_Ypoint_entry)
            if (not y): return
            t = ("rotate_other", v, (x, y), antiClockwise)
            message = "Rotated %d degrees by the point (%d, %d) %s" % (v, x, y, ("anti-clockwise" if (antiClockwise) else "clockwise"))

        self.transformation_list.append(t)
        self.transformation_listbox.insert("end", message)


    def verify_num_entry(self, entry) -> int|float|None:
        try:
            value = float(entry.get())
        except Exception:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value

    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)
