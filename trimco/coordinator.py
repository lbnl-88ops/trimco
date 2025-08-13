from typing import Any, List, Dict, Tuple
from logging import info
from pathlib import Path
import traceback

from trimco.gui.plot import PlotFrame
from trimco.gui.coil_settings import CoilSettingsCalculatedFrame, CoilSettingsFrame

from trimco.calc.field_profile import FieldProfile
from cyclotron.analysis.trim_coils import solve_coil_currents
from cyclotron.analysis.trim_coils.current_limits import _get_default_limits

import ttkbootstrap as ttk
import numpy as np

class Coordinator:
    def __init__(self, objects: List[Any]):
        self.attach(objects)
        self.field_profile = FieldProfile()
        self.calculated_field_profile = FieldProfile()
        self._coil_limits: Dict[int, Tuple[float | None, float]] = {
            n: _get_default_limits(n + 1) for n in range(17)
        }
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
        self._coil_settings.entUnbalance.config(validate='focusout', validatecommand=self.entry_update)
        for coil_setting in self._coil_settings_calculated.coil_settings.values():
            coil_setting.checkbox.config(command=self.checkbox_update)
            for entry in coil_setting.current_entries:
                entry.config(validate='focusout', validatecommand=self.current_limit_update)
        self._coil_settings.entMainCurrent.config(validate='focusout', 
                                                  validatecommand=self.update_main_current)
        self._coil_settings_calculated.set_current_limits(self._coil_limits)
        self._coil_settings_calculated.entUnbalanceDesired.config(validate='focusout', validatecommand=self.entry_update)
        self._update_field() 
        self._update_calculated_field()
        self.update_plot()

    def update_main_current(self) -> bool:
        try:
            self.entry_update()
            self.checkbox_update()
        except BaseException as e:
            print(f'Error updating main current: {traceback.print_exc()}')
            return False
        return True

    def entry_update(self) -> bool:
        try:
            self._update_field()
            self.update_plot()
            if self._use_trim_coils():
                self.checkbox_update()
        except BaseException as e:
            print(f'Error updating coil current: {traceback.print_exc()}')
            return False
        return True
    
    def current_limit_update(self) -> bool:
        try:
            self._coil_limits = self._coil_settings_calculated.current_limits()
        except BaseException as e:
            print(f'Error updating coil current limit: {traceback.print_exc()}')
            return False
        self.checkbox_update()
        return True

    def checkbox_update(self) -> bool:
        try:
            self._calculate_new_settings()
            self._update_calculated_field()
            self.update_plot()
        except BaseException as e:
            print(f'Error updating coil status: {traceback.print_exc()}')
            return False
        return True

    def _use_trim_coils(self) -> List[int]:
        return [n for n,v in self._coil_settings_calculated.use_trim_coils().items() if v]

    def _calculate_new_settings(self):
        trim_coils = self.calculated_field_profile.trim_coils
        desired_unbalance = float(self._coil_settings_calculated.unbalance_desired.get())
        if trim_coils is None:
            return
        for trim_coil in trim_coils:
            idx = trim_coil.number - 1
            if trim_coil.number == 1:
                limits = (self._coil_limits[idx][0], 
                          self._coil_limits[idx][1] - desired_unbalance/2)
            else:
                limits = self._coil_limits[idx]
            trim_coil.set_current_limits(limits) 

        use_coils_indexes = self._use_trim_coils()
        self._coil_settings_calculated.clear_current_settings()

        if use_coils_indexes:
            # increment coil index by 1 because solve coil currents expects number not index
            solved_currents = solve_coil_currents(self.field_profile.trim_coil_profile(),
                                                trim_coils,
                                                use_coils=[v + 1 for v in use_coils_indexes])
            if solved_currents is not None:
                # unbalance = self._coil_settings.unbalance
                self._plot.clear_warning()
                currents_to_set = {(c.number - 1): current for c, current in solved_currents.items()}
                if 0 in currents_to_set:
                    if abs(currents_to_set[0]) - desired_unbalance < 0:
                        self._plot.set_warning('Bad imbalance value')
                        return
                    currents_to_set[0] = currents_to_set[0] + np.sign(currents_to_set[0])*desired_unbalance/2
                self._coil_settings_calculated.set_current_settings(currents_to_set, desired_unbalance)
            else:
                self._plot.set_warning('Fit failed, try changing trim coil settings')

    def _update_field(self):
        self._update_field_profile(self.field_profile, self._coil_settings)

    def _update_calculated_field(self):
        self._update_field_profile(self.calculated_field_profile, self._coil_settings_calculated)

    def _update_field_profile(self, profile: FieldProfile, coil_settings: CoilSettingsFrame):
        coil_entries = {i: coil_settings.current(i) for i in range(17)}
        coil_entries[0] = coil_entries[0] - np.sign(coil_entries[0])*coil_settings.unbalance/2
        main_current = float(self._coil_settings.main_current.get())
        profile.update_profile(main_current, coil_entries)

    def update_plot(self):
        self._plot.clear_plot()
        r, field = self.field_profile.field_profile()
        r, caclculated_field = self.calculated_field_profile.field_profile()
        self._plot.plot_field(r, field, 'Current field')
        self._plot.plot_field(r, caclculated_field, 'Calculated field')