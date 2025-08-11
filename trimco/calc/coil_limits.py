from typing import Dict, List, Tuple

from cyclotron.analysis.model import TrimCoil
from cyclotron.analysis.trim_coils.current_limits import _get_default_limits


class CoilLimits:
    def __init__(self):
        self.current_limits: Dict[int, Tuple[float, float]] = {
            i: _get_default_limits(i + 1) for i in range(17)
    }
        # for coil in trim_coils:
            # if coil.number in use_trim_coils:
                # coil.set_current_limits(self.current_limits[coil.number])
            # else:
                # coil.set_current_limits((0, 0))

    
