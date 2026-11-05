"""
quantum_utils.py - Quantum Circuit Helpers and Identity Primitive
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT
from config import IDENTITY_SHOTS, IDENTITY_THRESHOLD


def run_identity_test(oracle, h_element: str, power_k: int, shots: int = IDENTITY_SHOTS) -> bool:
    qc = QuantumCircuit(1, 1)
    qc.h(0)
    
    gate = oracle.get_gate(h_element, power_k)
    qc.append(gate, [0])
    
    qc.h(0)
    qc.measure(0, 0)
    
    counts = oracle.run(qc, shots=shots)
    zero_count = counts.get('0', 0)
    
    return zero_count >= (shots * IDENTITY_THRESHOLD)

def collect_phase_samples(oracle, h_element: str, num_samples: int = 20) -> list:
    """
    Runs 16-qubit phase estimation to obtain phase estimates.
    """
    samples = []
    
    for _ in range(num_samples):
        qc = QuantumCircuit(16, 16)
        
        for j in range(8):
            qc.h(j)       # g control qubits
            qc.h(j + 8)   # h control qubits
            
        for j in range(8):
            gate_g = oracle.get_gate("g", 2**j).control(1)
            gate_h = oracle.get_gate(h_element, 2**j).control(1)
            
            qc.append(gate_g, [j] + list(range(16, 16)))
            qc.append(gate_h, [j + 8] + list(range(16, 16)))
            
        qft_inv = QFT(num_qubits=8, inverse=True).to_gate()
        qc.append(qft_inv, range(8))
        qc.append(qft_inv, range(8, 16))
        
        qc.measure(range(16), range(16))
        
        counts = oracle.run(qc, shots=1)
        bitstring = list(counts.keys())[0]
        
        x_val = int(bitstring[:8][::-1], 2)
        y_val = int(bitstring[8:][::-1], 2)
        
        samples.append((x_val / 256.0, y_val / 256.0))
        
    return samples