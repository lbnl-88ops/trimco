from typing import Any, List, Dict
from logging import info
from pathlib import Path

from trimco.gui.plot import PlotFrame
from trimco.gui.coil_settings import CoilSettingsCalculatedFrame, CoilSettingsFrame

from trimco.calc.field_profile import FieldProfile
from cyclotron.analysis.trim_coils import solve_coil_currents, update_current_limits

import numpy as np

class Coordinator:
    def __init__(self, objects: List[Any]):
        self.attach(objects)
        self.field_profile = FieldProfile()
        self.calculated_field_profile = FieldProfile()
        self.configure_objects()

    def attach(self, objects: List[Any]) -> None:
        for object in objects:
            match object:
                case PlotFrame():
                    self._plot = object
                case CoilSettingsCalculatedFrame():
                    self._coil_settings_calculated = object
                case CoilSettingsFrame():
                    self._coil_settings = object
                case _:
                    raise RuntimeError(f'Coordinator passed bad object {object}')

    def configure_objects(self):
        self._main_current = float(self._coil_settings.main_current.get())
        for entry in self._coil_settings.trim_coil_entries.values():
            entry.config(validate='focusout', validatecommand=self.update_currents)
        for checkbox in self._coil_settings_calculated.trim_coil_checkboxes.values():
            checkbox.config(command=self.update_currents)
        self._coil_settings.entMainCurrent.config(validate='focusout', 
                                                  validatecommand=self.update_currents)
        self.update_currents()

    def update_currents(self) -> bool:
        self._plot.clear_plot()
        try:
            main_current = float(self._coil_settings.main_current.get())
        except ValueError as e:
            print(e)
            return False
        self._update_field_profiles(main_current)
        self._calculate_new_settings()
        self._update_field_profiles(main_current)
        self.update_plot()
        return True

    def _use_trim_coils(self) -> List[int]:
        return [i for i in range(17) if self._coil_settings_calculated.use_trim_coil[i].get()]

    def _calculate_new_settings(self):
        trim_coils = self.calculated_field_profile.trim_coils
        if trim_coils is not None:
            print()
            update_current_limits(trim_coils, [v + 1 for v in self._use_trim_coils()])
            solved_currents = solve_coil_currents(self.field_profile.trim_coil_profile(),
                                                  trim_coils)
            if solved_currents is not None:
                self._plot.strWarning.set('')
                for coil, current in solved_currents.items():
                    self._coil_settings_calculated.coil_settings[coil.number - 1].set(current)
            else:
                self._plot.strWarning.set('Fit failed, try to add more trim coils.')

    def _update_field_profiles(self, main_current):
        coil_entries = {i: float(self._coil_settings.trim_coil_entries[i].get()) for i in range(17)}
        calculated_coil_entries = {i: float(self._coil_settings_calculated.coil_settings[i].get())
                                    for i in range(17)}
        for i in [coil for coil in calculated_coil_entries if coil not in self._use_trim_coils()]:
            calculated_coil_entries[i] = 0        

        self.field_profile.update_profile(main_current, coil_entries)
        self.calculated_field_profile.update_profile(main_current, calculated_coil_entries)

    def update_plot(self):
        r, field = self.field_profile.field_profile()
        r, caclculated_field = self.calculated_field_profile.field_profile()
        self._plot.plot_field(r, field, 'Current field')
        self._plot.plot_field(r, caclculated_field, 'Calculated field')