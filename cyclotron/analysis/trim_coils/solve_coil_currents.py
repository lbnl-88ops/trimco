from typing import Dict, List
from logging import getLogger

import numpy as np
from scipy.optimize import minimize

from cyclotron.analysis.model import TrimCoil

_log = getLogger(__name__)

def solve_coil_currents(
        field: np.ndarray, 
        trim_coils: List[TrimCoil]) -> Dict[TrimCoil, float] | None:
    solved_currents: Dict[TrimCoil, float] = {}
    k = len(field)
    bounds = []

    sorted_coils = sorted(trim_coils, key=lambda x: x.number)
    A = np.zeros((len(trim_coils), k))
    for i, coil in enumerate(sorted_coils):
        bounds.append(coil.current_limits)
        A[i, :] = coil.db_di()[:k]

    def residual(x) -> float: 
        r = np.power(field - np.einsum('ij,i->j', A, x), 2)
        weights = np.array([10,10,10,10,10,10,10,10,10,10,10,
                  11,12,13,14,15,16,17,18,19,20,21,22,
                  23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39] + 15*[0])[:k]
        return float(np.sqrt(np.sum(weights * r)))

    result = minimize(residual, np.zeros((len(trim_coils))), bounds=bounds)    
    if not result['success']:
        _log.warning('Trim coil fit failed')
        return None
    x = result['x']
    for i, current in enumerate(x):
        solved_currents[sorted_coils[i]] = current

    return solved_currents
