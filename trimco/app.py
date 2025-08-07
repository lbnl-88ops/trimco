import ttkbootstrap as ttk

from trimco.gui.coil_settings import CoilSettingsFrame

class TrimcoApp(ttk.Window):
    def __init__(self):
        super().__init__(title='Trimco')
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.create_widgets()

    def create_widgets(self):
        self.coil_settings = CoilSettingsFrame(self)

        self.coil_settings.pack(side='left')

    def quit(self):
        self.destroy()
