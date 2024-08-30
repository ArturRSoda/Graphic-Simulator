import tkinter as tk

class Frame(tk.Frame):
    def __init__(self, parent, width: int, height: int):
        super().__init__(parent, width=width, height=height, borderwidth=3, relief="groove")


class Label(tk.Label):
    def __init__(self, parent, text: str, size: int):
        super().__init__(parent, text=text, font=("Helvetica", size))


class CGSystem():
    def __init__(self) -> None:
        self.app = tk.Tk()
        self.app.title("Computer Graphics System")
        self.app.geometry("1024x735")

        self.menu_frame        : Frame
        self.object_menu_frame : Frame
        self.window_menu_frame : Frame
        self.portview_frame    : Frame
        self.messageBox_frame  : Frame
        self.messageBox        : tk.Listbox
        self.objects_list      : tk.Listbox
        self.canvas            : tk.Canvas
        self.portview_width    : int
        self.portview_height   : int

        self.add_menu()
        self.add_portview()
        self.add_messagesBox()

    def run(self):
        self.app.mainloop()

    def add_portview(self):
        self.app.update()
        width = self.app.winfo_width()-self.menu_frame.winfo_width()-20
        self.portview_frame = Frame(self.app, width, 500)
        self.portview_frame.place(x=self.menu_frame.winfo_width()+20, y=10)

        Label(self.portview_frame, "Portview", 10).place(x=10, y=10)

        self.app.update()
        self.portview_height = self.portview_frame.winfo_height()-70
        self.portview_width = self.portview_frame.winfo_width()-35
        self.canvas = tk.Canvas(self.portview_frame, width=self.portview_width, height=self.portview_height, bg="white", borderwidth=5, relief="groove")
        self.canvas.place(x=10, y=30)

    def add_messagesBox(self):
        self.app.update()
        width = self.app.winfo_width()-self.menu_frame.winfo_width()-20
        self.messageBox_frame = Frame(self.app, width, 200)
        self.messageBox_frame.place(x=self.menu_frame.winfo_width()+20, y=self.portview_frame.winfo_height()+20)

        self.app.update()
        self.messageBox = tk.Listbox(self.messageBox_frame, width=75, height=9)
        self.messageBox.place(x=10, y=10)


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

        self.objects_list = tk.Listbox(self.object_menu_frame, width=26, height=5)
        self.objects_list.place(x=10, y=30)

        tk.Button(self.object_menu_frame, text="Add", command=self.add_object).place(x=45, y=135)
        tk.Button(self.object_menu_frame, text="Del", command=self.del_object).place(x=145, y=135)

    def add_object(self):
        self.add_message("Added object")

    def del_object(self):
        self.add_message("Deleted object")


    def add_window_menu(self):
        self.window_menu_frame = Frame(self.menu_frame, self.menu_frame.winfo_width()-26, 180)
        self.window_menu_frame.place(x=10, y=200)

        Label(self.window_menu_frame, "Window", 10).place(x=10, y=10)

        tk.Button(self.window_menu_frame, text="Up", command=self.move_window_up).place(x=40, y=40)
        tk.Button(self.window_menu_frame, text="Left", command=self.move_window_left).place(x=10, y=70)
        tk.Button(self.window_menu_frame, text="Right", command=self.move_window_right).place(x=62, y=70)
        tk.Button(self.window_menu_frame, text="Down", command=self.move_window_down).place(x=30, y=100)

        tk.Button(self.window_menu_frame, text="Zoom In", command=self.zoom_window_in).place(x=150, y=50)
        tk.Button(self.window_menu_frame, text="Zoom Out", command=self.zoom_window_out).place(x=150, y=90)

    def move_window_up(self):
        self.add_message("window moved up")

    def move_window_down(self):
        self.add_message("window moved down")

    def move_window_left(self):
        self.add_message("window moved left")

    def move_window_right(self):
        self.add_message("window moved right")

    def zoom_window_in(self):
        self.add_message("window zoomed in")

    def zoom_window_out(self):
        self.add_message("window zoomed out")


    def add_message(self, message: str):
        self.messageBox.insert(0, message)



sys = CGSystem()
sys.run()
