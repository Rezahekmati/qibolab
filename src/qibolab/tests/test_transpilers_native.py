import numpy as np
import pytest
from qibo import gates
from qibo.backends import NumpyBackend
from qibo.models import Circuit
from scipy.linalg import expm

from qibolab.transpilers.native import NativeGates


def assert_matrices_allclose(gate, phase=1):
    backend = NumpyBackend()
    native_gates = NativeGates()
    target_matrix = gate.asmatrix(backend)
    # Remove global phase from target matrix
    target_unitary = target_matrix / np.power(
        np.linalg.det(target_matrix), 1 / float(target_matrix.shape[0]), dtype=complex
    )
    circuit = Circuit(len(gate.qubits))
    circuit.add(native_gates.translate_gate(gate))
    native_matrix = circuit.unitary(backend)
    # Remove global phase from native matrix
    native_unitary = native_matrix / np.power(
        np.linalg.det(native_matrix), 1 / float(native_matrix.shape[0]), dtype=complex
    )
    np.testing.assert_allclose(native_unitary, target_unitary, atol=1e-12)


@pytest.mark.parametrize("gatename", ["H", "X", "Y"])
def test_pauli_to_native(gatename):
    backend = NumpyBackend()
    gate = getattr(gates, gatename)(0)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("gatename", ["RX", "RY", "RZ"])
def test_rotations_to_native(gatename):
    gate = getattr(gates, gatename)(0, theta=0.1)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("gatename", ["S", "SDG", "T", "TDG"])
def test_special_single_qubit_to_native(gatename):
    gate = getattr(gates, gatename)(0)
    assert_matrices_allclose(gate)


def test_u1_to_native():
    gate = gates.U1(0, theta=0.5)
    assert_matrices_allclose(gate)


def test_u2_to_native():
    gate = gates.U2(0, phi=0.1, lam=0.3)
    assert_matrices_allclose(gate)


def test_u3_to_native():
    gate = gates.U3(0, theta=0.2, phi=0.1, lam=0.3)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("gatename", ["CNOT", "CZ", "SWAP", "FSWAP"])
def test_two_qubit_to_native(gatename):
    gate = getattr(gates, gatename)(0, 1)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("gatename", ["CRX", "CRY", "CRZ"])
def test_controlled_rotations_to_native(gatename):
    gate = getattr(gates, gatename)(0, 1, 0.3)
    assert_matrices_allclose(gate)


def test_cu1_to_native():
    gate = gates.CU1(0, 1, theta=0.4)
    assert_matrices_allclose(gate)


def test_cu2_to_native():
    gate = gates.CU2(0, 1, phi=0.2, lam=0.3)
    assert_matrices_allclose(gate)


def test_cu3_to_native():
    gate = gates.CU3(0, 1, theta=0.2, phi=0.3, lam=0.4)
    assert_matrices_allclose(gate)


def test_fSim_to_native():
    gate = gates.fSim(0, 1, theta=0.3, phi=0.1)
    assert_matrices_allclose(gate)


def test_GeneralizedfSim_to_native():
    from qibolab.tests.test_transpilers_decompositions import random_unitary

    unitary = random_unitary(1)
    gate = gates.GeneralizedfSim(0, 1, unitary, phi=0.1)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("gatename", ["RXX", "RYY", "RZZ"])
def test_rnn_to_native(gatename):
    gate = getattr(gates, gatename)(0, 1, theta=0.1)
    assert_matrices_allclose(gate)


def test_TOFFOLI_to_native():
    gate = gates.TOFFOLI(0, 1, 2)
    assert_matrices_allclose(gate)


@pytest.mark.parametrize("nqubits", [1, 2])
def test_unitary_to_native(nqubits):
    from qibolab.tests.test_transpilers_decompositions import random_unitary

    u = random_unitary(nqubits)
    # transform to SU(2^nqubits) form
    u = u / np.sqrt(np.linalg.det(u))
    gate = gates.Unitary(u, *range(nqubits))
    assert_matrices_allclose(gate)
