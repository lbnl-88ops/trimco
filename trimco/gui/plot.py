from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import ttkbootstrap as ttk
import numpy as np


class Plot(ttk.Frame):
    def __init__(self, owner):
        super().__init__(owner)
        self.create_plot()
        self.create_widgets()

    def create_widgets(self):
        self.canvas = FigureCanvasTkAgg(self._fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_plot(self):
        self._fig = Figure((9,6), tight_layout=True)
        ax = self._fig.gca()
        ax.set_xlabel('Radius (in)')
        ax.set_ylabel('B (kG)')
        ax.set_xlim(0, 60)

    def plot_field(self, r_values: np.ndarray, field: np.ndarray, label: str) -> None:
        ax = self._fig.gca()
        ax.plot(r_values, field, label=label, ls='--')
        self.canvas.draw()

    def clear_plot(self) -> None:
        self._fig.gca().cla()
