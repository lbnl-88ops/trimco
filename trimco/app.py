import ttkbootstrap as ttk

from .coordinator import Coordinator
from trimco.gui.coil_settings import CoilSettingsFrame, CoilSettingsCalculatedFrame
from trimco.gui.plot import PlotFrame

class TrimcoApp(ttk.Window):
    def __init__(self):
        super().__init__(title='Trimco')
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.create_widgets()

    def create_widgets(self):
        self.coil_settings = CoilSettingsFrame(self)
        self.plot = PlotFrame(self)
        self.coil_settings_calculated = CoilSettingsCalculatedFrame(self)

        self.coil_settings.pack(side='top')
        self.plot.pack(side='top')
        self.coil_settings_calculated.pack(side='top')
        self.coordinator = Coordinator([self.plot, self.coil_settings])

    def quit(self):
        self.destroy()
