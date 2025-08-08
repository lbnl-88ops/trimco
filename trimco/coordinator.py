from typing import Any, List
from logging import info
from pathlib import Path

from trimco.gui.plot import PlotFrame
from trimco.gui.coil_settings import CoilSettingsFrame

from trimco.calc.field_profile import FieldProfile

import numpy as np

class Coordinator:
    def __init__(self, objects: List[Any]):
        self.attach(objects)
        self.configure_objects()
        self.field_profile = FieldProfile()

    def attach(self, objects: List[Any]) -> None:
        for object in objects:
            match object:
                case PlotFrame():
                    self._plot = object
                case CoilSettingsFrame():
                    self._coil_settings = object
                case _:
                    raise RuntimeError(f'Coordinator passed bad object {object}')

    def configure_objects(self):
        self._main_current = float(self._coil_settings.main_current.get())
        for entry in self._coil_settings.trim_coil_entries.values():
            entry.config(validate='focusout', validatecommand=self.update_currents)
        self._coil_settings.entMainCurrent.config(
            validate='focusout', validatecommand=self.update_currents
        )

    def update_currents(self) -> bool:
        self._plot.clear_plot()
        try:
            self.field_profile.update_profile(float(self._coil_settings.main_current.get()),
                                              {i: float(self._coil_settings.trim_coil_entries[i].get()) for i in range(17)})
        except ValueError as e:
            print(e)
            return False
        except RuntimeError as e:
            print(e)
            return False
        self.update_plot()
        return True

    def update_plot(self):
        r, field = self.field_profile.field_profile()
        self._plot.plot_field(r, field, 'Current field')