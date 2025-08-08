from pathlib import Path
from typing import Dict, Tuple

import numpy as np

from cyclotron.analysis.io import (build_iron_field_from_file, 
                                   read_trim_coil_data,
                                   calculate_trim_coil_fields)

class FieldProfile:
    def __init__(self):
        self._main_current: float = 0
        self._trim_coil_currents: Dict[int, float] = {}

        self._main_field_path = Path('./data/fieldmap.txt')
        self._trim_coil_data = read_trim_coil_data(Path('./data/TAPEIN.TXT'))
        self._iron_field = None
        self.trim_coils = None
        self._trim_coil_fields = None
        self._max_r = 40

    def _set_main_current(self, to_set: float) -> None:
        if to_set != self._main_current:
            self._main_current = to_set
            self._iron_field = build_iron_field_from_file(to_set, self._main_field_path)
            self.trim_coils = calculate_trim_coil_fields(self._trim_coil_data, to_set)
            self._trim_coil_currents = {i: 0 for i in range(len(self.trim_coils))}
            self._trim_coil_fields = np.zeros(shape=(len(self.trim_coils), self._max_r))

    def _set_trim_coil(self, trim_coil_index: int, current: float) -> None:
        if self.trim_coils is None or self._trim_coil_fields is None:
            raise RuntimeError
        if current != self._trim_coil_currents[trim_coil_index]:
            b_field = self.trim_coils[trim_coil_index].b_field(current)
            self._trim_coil_fields[trim_coil_index,:] = b_field[:self._max_r]

    def update_profile(self, main_current: float, trim_coil_currents: Dict[int, float]):
        self._set_main_current(main_current)
        for coil, current in trim_coil_currents.items():
            self._set_trim_coil(coil, current)
        self._trim_coil_currents = trim_coil_currents


    def field_profile(self) -> Tuple[np.ndarray, np.ndarray]:
        if self._iron_field is None or self._trim_coil_fields is None:
            raise RuntimeError
        return (np.asarray(self._iron_field.r_values[:self._max_r]), 
                self._iron_field.first_moment()[:self._max_r] + self.trim_coil_profile())

    def trim_coil_profile(self) -> np.ndarray:
        if self._trim_coil_fields is None:
            raise RuntimeError
        return np.sum(self._trim_coil_fields, axis=0)


