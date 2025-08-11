from typing import Any, List, Dict
from logging import info
from pathlib import Path

from trimco.gui.plot import PlotFrame
from trimco.gui.coil_settings import CoilSettingsCalculatedFrame, CoilSettingsFrame

from trimco.calc.field_profile import FieldProfile
from trimco.calc.coil_limits import CoilLimits
from cyclotron.analysis.trim_coils import solve_coil_currents, update_current_limits

import numpy as np

class Coordinator:
    def __init__(self, objects: List[Any]):
        self.attach(objects)
        self.field_profile = FieldProfile()
        self.calculated_field_profile = FieldProfile()
        self._coil_limits = CoilLimits()
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
        for entry in [s.entry for s in self._coil_settings.coil_settings.values()]:
            entry.config(validate='focusout', validatecommand=self.entry_update)
        for checkbox in [s.checkbox for s in self._coil_settings_calculated.coil_settings.values()
                         if s.checkbox is not None]:
            checkbox.config(command=self.checkbox_update)
        self._coil_settings.entMainCurrent.config(validate='focusout', 
                                                  validatecommand=self.update_main_current)
        self._update_field() 
        self._update_calculated_field()
        self._update_current_limits()
        self.update_plot()

    def update_main_current(self) -> bool:
        try:
            self.entry_update()
            self.checkbox_update()
        except BaseException:
            return False
        return True

    def entry_update(self) -> bool:
        try:
            self._update_field()
            self.update_plot()
            if self._use_trim_coils():
                self.checkbox_update()
        except BaseException:
            return False
        return True

    def checkbox_update(self) -> bool:
        try:
            self._update_current_limits()
            self._calculate_new_settings()
            self._update_calculated_field()
            self.update_plot()
        except BaseException:
            return False
        return True

    def _use_trim_coils(self) -> List[int]:
        return self._coil_settings_calculated.use_trim_coils()

    def _update_current_limits(self):
        trim_coils = self.calculated_field_profile.trim_coils
        if trim_coils is None:
            info('Attempted to update trim coil max currents but no trim coils')
            return
        for trim_coil in trim_coils:
            trim_coil.set_current_limits(self._coil_limits.current_limits[trim_coil.number - 1])
            coil_settings = self._coil_settings_calculated.coil_settings[trim_coil.number - 1]
            if coil_settings.max_current is not None:
                coil_settings.max_current.set(f'{trim_coil.current_limits[1]:.0f}')
            if coil_settings.min_current is not None:
                coil_settings.min_current.set(f'{trim_coil.current_limits[0]:.0f}')


    def _calculate_new_settings(self):
        trim_coils = self.calculated_field_profile.trim_coils
        if trim_coils is not None:
            for setting in self._coil_settings_calculated.coil_settings.values():
                setting.setting.set('0')
            use_coils = self._coil_settings_calculated.use_trim_coils()
            if use_coils:
                solved_currents = solve_coil_currents(self.field_profile.trim_coil_profile(),
                                                    trim_coils,
                                                    use_coils=use_coils)
                if solved_currents is not None:
                    self._plot.strWarning.set('')

                    for trim_coil, current in solved_currents.items():
                        idx = trim_coil.number - 1
                        self._coil_settings_calculated.coil_settings[idx].setting.set(f'{current:.0f}')
                else:
                    self._plot.strWarning.set('Fit failed, try to add more trim coils.')

    def _update_field(self):
        self._update_field_profile(self.field_profile, self._coil_settings)

    def _update_calculated_field(self):
        self._update_field_profile(self.calculated_field_profile, self._coil_settings_calculated)

    def _update_field_profile(self, profile: FieldProfile, coil_settings: CoilSettingsFrame):
        coil_entries = {i: coil_settings.current(i) for i in range(17)}
        main_current = float(self._coil_settings.main_current.get())
        profile.update_profile(main_current, coil_entries)

    def update_plot(self):
        self._plot.clear_plot()
        r, field = self.field_profile.field_profile()
        r, caclculated_field = self.calculated_field_profile.field_profile()
        self._plot.plot_field(r, field, 'Current field')
        self._plot.plot_field(r, caclculated_field, 'Calculated field')