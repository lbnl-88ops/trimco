from typing import Dict, List, Optional
from logging import getLogger

import numpy as np
from scipy.optimize import minimize

from cyclotron.analysis.model import TrimCoil

_log = getLogger(__name__)

def solve_coil_currents(
        field: np.ndarray, 
        trim_coils: List[TrimCoil],
        *,
        use_coils: Optional[List[int]] = None) -> Dict[TrimCoil, float] | None:
    if use_coils is None:
        use_coils = [coil.number for coil in trim_coils]
    use_coils = sorted(use_coils)

    solved_currents: Dict[TrimCoil, float] = {}
    k = len(field)
    bounds = []
    constraints = []

    sorted_coils = [coil for coil in sorted(trim_coils, key=lambda x: x.number)
                    if coil.number in use_coils]

    A = np.zeros((len(sorted_coils), k))

    for i, coil in enumerate(sorted_coils):
        min_current, max_current = coil.current_limits
        if min_current is None:
            min_current = -max_current
        else:
            constraints.append({'type': 'ineq', 'fun': lambda x, i=i, min_current=min_current: abs(x[i]) - min_current})
            min_current = -max_current

        bounds.append((min_current, max_current))
        A[i, :] = coil.db_di()[:k]

    def residual(x) -> float: 
        r = np.power(field - np.einsum('ij,i->j', A, x), 2)
        weights = np.array([10,10,10,10,10,10,10,10,10,10,10,
                  11,12,13,14,15,16,17,18,19,20,21,22,
                  23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39] + 15*[0])[:k]
        return float(np.sqrt(np.sum(weights * r)))
    result = minimize(residual, np.zeros((len(sorted_coils))), bounds=bounds, 
                      constraints=constraints)    
    if not result['success']:
        _log.warning('Trim coil fit failed')
        return None
    x = result['x']
    for i, current in enumerate(x):
        coil = sorted_coils[i]
        if coil.number in use_coils:
            solved_currents[coil] = current
        else:
            solved_currents[coil] = 0

    return solved_currents
