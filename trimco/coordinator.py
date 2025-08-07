from typing import Any, List
from pathlib import Path

from trimco.gui.plot import Plot
from trimco.gui.coil_settings import CoilSettingsFrame

from cyclotron.analysis.io import build_iron_field_from_file

import numpy as np

class Coordinator:
    def __init__(self, objects: List[Any]):
        self.attach(objects)
        self.configure_objects()
        self._main_field_path = Path('./data/fieldmap.txt')

    def attach(self, objects: List[Any]) -> None:
        for object in objects:
            match object:
                case Plot():
                    self._plot = object
                case CoilSettingsFrame():
                    self._coil_settings = object
                case _:
                    raise RuntimeError(f'Coordinator passed bad object {object}')

    def configure_objects(self):
        self._main_current = float(self._coil_settings.main_current.get())
        self._coil_settings.entMainCurrent.config(
            validate='focusout', validatecommand=self.update_main_current
        )

    def update_main_current(self) -> bool:
        self._plot.clear_plot()
        try:
            main_current = float(self._coil_settings.main_current.get())
        except ValueError:
            return False
        try:
            iron_field = build_iron_field_from_file(main_current, self._main_field_path)
        except RuntimeError:
            return False
        self._plot.plot_field(np.array(iron_field.r_values), 
                              iron_field.first_moment(), 'Iron-field')
        return True