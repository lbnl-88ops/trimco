from typing import Dict, List, Tuple

from cyclotron.analysis.model import TrimCoil
from cyclotron.analysis.trim_coils.current_limits import _get_default_limits


class CoilLimits:
    def __init__(self):
        self.current_limits: Dict[int, Tuple[float | None, float]] = {}
        self.set_default()

    def set_default(self):
        self.current_limits = {i: _get_default_limits(i + 1) for i in range(17)}

    def set_limits(self, idx: int, min: float | None, max: float):
        self.current_limits[idx] = (min, max)

