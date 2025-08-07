import ttkbootstrap as ttk

class TrimcoApp(ttk.Window):
    def __init__(self):
        super().__init__(title='Trimco')
        self.protocol("WM_DELETE_WINDOW", self.quit)

    def quit(self):
        self.destroy()
