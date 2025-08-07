import ttkbootstrap as ttk

from trimco.gui.coil_settings import CoilSettingsFrame
from trimco.gui.plot import Plot

class TrimcoApp(ttk.Window):
    def __init__(self):
        super().__init__(title='Trimco')
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.create_widgets()

    def create_widgets(self):
        self.coil_settings = CoilSettingsFrame(self)
        self.plot = Plot(self)

        self.coil_settings.pack(side='top')
        self.plot.pack(side='top')

    def quit(self):
        self.destroy()
