"""
solver.py - Order Finding & Discrete Log Solver
"""

from sympy.matrices import Matrix
from quantum_utils import run_identity_test, collect_phase_samples


def find_order(oracle, g_element: str = "g") -> int:
    """
    Finds N = ord(g) via exponential search and binary search using identity tests.
    """
    k = 1
    while not run_identity_test(oracle, g_element, k):
        k *= 2
        if k > (1 << 60):
            raise RuntimeError("Order exceeds 2^60 or forgery.")
            
    lo, hi = k // 2, k
    while lo < hi:
        mid = (lo + hi) // 2
        if run_identity_test(oracle, g_element, mid):
            hi = mid
        else:
            lo = mid + 1
            
    return lo


def solve_discrete_log_classical(oracle, h_element: str, N: int):
    for x in range(N):
        if run_identity_test(oracle, f"{h_element}_g_-{x}", 1):
            return x
    return None


def solve_discrete_log_lll(oracle, h_element: str, N: int):
    samples = collect_phase_samples(oracle, h_element, num_samples=20)
    rows = [[int(x_g * 256), int(y_h * 256)] for x_g, y_h in samples]
    
    # Process lattice using SymPy / fpylll
    candidate_x = 0  # Replaced by LLL output
    
    if run_identity_test(oracle, f"{h_element}_g_-{candidate_x}", 1):
        return candidate_x
    return None


def find_discrete_log(oracle, h_element: str, N: int):
    if N <= (1 << 16):
        return solve_discrete_log_classical(oracle, h_element, N)
    return solve_discrete_log_lll(oracle, h_element, N)


def solve(oracle) -> dict:
    N = find_order(oracle, "g")
    
    logs = {}
    for name in ["A", "B", "C"]:
        x = find_discrete_log(oracle, name, N)
        if x is None:
            return {"order": N, "secret": "none"}
        logs[name] = x
        
    secret = (logs["A"] * logs["B"] * logs["C"]) % N
    return {"order": N, "secret": secret}


class MockOracle:
    """Mock device for local testing"""
    def run(self, qc, shots=1):
        return {'0' * qc.num_qubits: shots}

    def get_gate(self, element, power):
        from qiskit.circuit.library import XGate
        return XGate()  # Removed .to_gate() call


if __name__ == "__main__":
    # Test with local MockOracle:
    oracle = MockOracle()
    result = solve(oracle)
    print("Challenge Result:", result)