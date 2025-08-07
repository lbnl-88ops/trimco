from pathlib import Path
from typing import Tuple

import numpy as np

from cyclotron.analysis.io import build_iron_field_from_file

class FieldProfile:
    def __init__(self):
        self._main_current: float = 0
        self._main_field_path = Path('./data/fieldmap.txt')
        self._iron_field = None

    def set_main_current(self, to_set: float) -> None:
        if to_set != self._main_current:
            self._main_current = to_set
            self._iron_field = build_iron_field_from_file(to_set, self._main_field_path)

    def field_profile(self) -> Tuple[np.ndarray, np.ndarray]:
        if self._iron_field is None:
            raise RuntimeError
        return (np.asarray(self._iron_field.r_values), 
                self._iron_field.first_moment())
        


        