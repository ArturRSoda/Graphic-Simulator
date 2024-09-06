import tkinter as tk
from tkinter import messagebox

class Frame(tk.Frame):
    def __init__(self, parent, width: int, height: int):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="groove")

class Label(tk.Label):
    def __init__(self, parent, text: str, size: int):
        super().__init__(parent, text=text, font=("Helvetica", size))

class CGSystemInterface():
    def __init__(self, system):
        self.menu_frame        : Frame
        self.object_menu_frame : Frame
        self.window_menu_frame : Frame
        self.canvas_frame      : Frame
        self.messageBox_frame  : Frame
        self.messageBox        : tk.Listbox
        self.objects_listbox   : tk.Listbox
        self.canvas            : tk.Canvas
        self.offset_var        : tk.IntVar
        self.offset_entry      : tk.Entry
        self.zoom_factor_var   : tk.DoubleVar
        self.Wcoord_var        : tuple[tk.IntVar, tk.IntVar]
        self.zoom_factor_entry : tk.Entry
        self.canvas_width      : int
        self.canvas_height     : int

        self.app = tk.Tk()
        self.app.title("Computer Graphics System")
        self.app.geometry("1000x700")
        self.system = system

        self.add_menu()
        self.add_canvas()
        self.add_messagesBox()

    def add_canvas(self):
        self.app.update()

        self.canvas_frame = Frame(self.app, self.app.winfo_width()-self.menu_frame.winfo_width()-20, 500)
        self.canvas_frame.place(x=self.menu_frame.winfo_width()+20, y=10)

        Label(self.canvas_frame, "Viewport", 10).place(x=10, y=10)

        self.app.update()
        self.canvas_width = self.canvas_frame.winfo_width()-35
        self.canvas_height = self.canvas_frame.winfo_height()-70
        self.canvas = tk.Canvas(self.canvas_frame, width=self.canvas_width, height=self.canvas_height, bg="white", borderwidth=5, relief="groove")
        self.canvas.place(x=10, y=30)

    def clear_canvas(self):
        self.canvas.delete("all")

    def add_menu(self):
        self.app.update()
        self.menu_frame = Frame(self.app, 300, self.app.winfo_height()-20)
        self.menu_frame.place(x=10, y=10)

        self.app.update()
        self.add_object_menu()
        self.add_window_menu()


    def add_object_menu(self):
        self.object_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 180)
        self.object_menu_frame.place(x=10, y=10)

        Label(self.object_menu_frame, "Objects", 10).place(x=10, y=10)

        self.objects_listbox = tk.Listbox(self.object_menu_frame, width=26, height=5)
        self.objects_listbox.place(x=10, y=30)

        tk.Button(self.object_menu_frame, text="Add", command=self.system.add_object).place(x=45, y=135)
        tk.Button(self.object_menu_frame, text="Del", command=self.del_object).place(x=145, y=135)

    def add_window_menu(self):
        self.window_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 220)
        self.window_menu_frame.place(x=10, y=200)

        Label(self.window_menu_frame, "Controls", 10).place(x=10, y=10)

        tk.Button(self.window_menu_frame, text="Up", command=self.move_up).place(x=40, y=40)
        tk.Button(self.window_menu_frame, text="Left", command=self.move_left).place(x=10, y=70)
        tk.Button(self.window_menu_frame, text="Right", command=self.move_right).place(x=62, y=70)
        tk.Button(self.window_menu_frame, text="Down", command=self.move_down).place(x=30, y=100)

        tk.Button(self.window_menu_frame, text="Zoom In", command=self.zoom_in).place(x=150, y=50)
        tk.Button(self.window_menu_frame, text="Zoom Out", command=self.zoom_out).place(x=150, y=90)

        tk.Button(self.window_menu_frame, text="Set Coord", command=self.set_window_coord).place(x=80, y=170)

        Label(self.window_menu_frame, "offset", 10).place(x=10, y=140)
        self.offset_var = tk.IntVar()
        self.offset_var.set(10)
        self.offset_entry = tk.Entry(self.window_menu_frame, textvariable=self.offset_var, width=4)
        self.offset_entry.place(x=50, y=140)

        Label(self.window_menu_frame, "zoom factor", 10).place(x=115, y=140)
        self.zoom_factor_var = tk.DoubleVar()
        self.zoom_factor_var.set(2.0)
        self.zoom_factor_entry = tk.Entry(self.window_menu_frame, textvariable=self.zoom_factor_var, width=4)
        self.zoom_factor_entry.place(x=200, y=140)
        

    def del_object(self):
        tp = self.objects_listbox.curselection()
        if (not tp):
            self.send_error("Select an item", "Please select an item to delte!")
            return

        id = tp[0]
        self.system.del_object(id)

    def set_window_coord(self):
        app = tk.Toplevel()
        app.title("Set Coordinates")
        app.geometry("180x150")

        Label(app, "Coordinates", 10).place(x=10, y=10)

        fm = Frame(app, width=160, height=50)
        fm.place(x=10, y=30)

        self.Wcoord_var = (tk.IntVar(), tk.IntVar())

        Label(fm, "X:", 10).place(x=10, y=15)
        tk.Entry(fm, textvariable=self.Wcoord_var[0], width=4).place(x=30, y=10)
        Label(fm, "Y:", 10).place(x=80, y=15)
        tk.Entry(fm, textvariable=self.Wcoord_var[1], width=4).place(x=100, y=10)

        tk.Button(app, text="Set", command=self.set_Wcoord).place(x=20, y=90)
        tk.Button(app, text="Cancel", command=app.destroy).place(x=80, y=90)

    def set_Wcoord(self):
        coord_x = self.verify_num_entry(self.Wcoord_var[0])
        coord_y = self.verify_num_entry(self.Wcoord_var[1])

        if (coord_x is not None) and (coord_y is not None):
            self.system.set_window_coord((coord_x, coord_y))


    def add_messagesBox(self):
        self.app.update()
        width = self.app.winfo_width()-self.menu_frame.winfo_width()-20
        height = self.app.winfo_height()-self.canvas_frame.winfo_height()-30
        self.messageBox_frame = Frame(self.app, width, height)
        self.messageBox_frame.place(x=self.menu_frame.winfo_width()+20, y=self.canvas_frame.winfo_height()+20)

        self.app.update()
        self.messageBox = tk.Listbox(self.messageBox_frame, width=72, height=8)
        self.messageBox.place(x=10, y=10)

    def move_up(self):
        offset = self.verify_num_entry(self.offset_var)
        if (offset is not None):
            self.system.move_window_up(offset)

    def move_down(self):
        offset = self.verify_num_entry(self.offset_var)
        if (offset is not None):
            self.system.move_window_down(offset)

    def move_left(self):
        offset = self.verify_num_entry(self.offset_var)
        if (offset is not None):
            self.system.move_window_left(offset)

    def move_right(self):
        offset = self.verify_num_entry(self.offset_var)
        if (offset is not None):
            self.system.move_window_right(offset)

    def zoom_in(self):
        zoom_factor = self.verify_num_entry(self.zoom_factor_var)
        if (zoom_factor is not None):
            self.system.zoom_window_in(zoom_factor)

    def zoom_out(self):
        zoom_factor = self.verify_num_entry(self.zoom_factor_var)
        if (zoom_factor is not None):
            self.system.zoom_window_out(zoom_factor)

    def verify_num_entry(self, entry) -> int|None:
        try:
            value = entry.get()
        except Exception:
            self.send_error("Value Error", "Please enter a numeric value on entry")
        else:
            return value

    def send_error(self, title: str, message: str):
        messagebox.showerror(title, message)

