"""Helper methods for loading and saving to runcards.

The format of runcards in the ``qiboteam/qibolab_platforms_qrc``
repository is assumed here. See :ref:`Using runcards <using_runcards>`
example for more details.
"""
from pathlib import Path
from typing import Tuple

import yaml

from qibolab.native import SingleQubitNatives, TwoQubitNatives
from qibolab.platform import PlatformSettings, QubitMapType, QubitPairMapType
from qibolab.qubits import Qubit, QubitPair


def load_runcard(path: Path) -> dict:
    """Load runcard YAML to a dictionary."""
    return yaml.safe_load(path.read_text())


def load_settings(runcard: dict) -> PlatformSettings:
    """Load platform settings section from the runcard."""
    return PlatformSettings(**runcard["settings"])


def load_qubits(runcard: dict) -> Tuple[QubitMapType, QubitPairMapType]:
    """Load qubits and pairs from the runcard.

    Uses the native gate and characterization sections of the runcard
    to parse the :class:`qibolab.qubits.Qubit` and :class:`qibolab.qubits.QubitPair`
    objects.
    """
    qubits = {q: Qubit(q, **char) for q, char in runcard["characterization"]["single_qubit"].items()}

    pairs = {}
    for pair in runcard["topology"]:
        pair = tuple(sorted(pair))
        pairs[pair] = QubitPair(qubits[pair[0]], qubits[pair[1]])

    # register single qubit native gates to ``Qubit`` objects
    native_gates = runcard.get("native_gates", {})
    for q, gates in native_gates.get("single_qubit", {}).items():
        qubits[q].native_gates = SingleQubitNatives.from_dict(qubits[q], gates)
    # register two-qubit native gates to ``QubitPair`` objects
    for pair, gatedict in native_gates.get("two_qubit", {}).items():
        pair = tuple(sorted(int(q) if q.isdigit() else q for q in pair.split("-")))
        pairs[pair].native_gates = TwoQubitNatives.from_dict(qubits, gatedict)

    return qubits, pairs


def dump_qubits(qubits: QubitMapType, pairs: QubitPairMapType) -> dict:
    """Dump qubit and pair objects to a dictionary following the runcard format."""
    native_gates = {
        "topology": [list(pair) for pair in pairs],
        "single_qubit": {q: qubit.native_gates.raw for q, qubit in qubits.items()},
        "two_qubit": {},
    }
    # add two-qubit native gates
    for p, pair in pairs.items():
        natives = pair.native_gates.raw
        if len(natives) > 0:
            native_gates["two_qubit"][f"{p[0]}-{p[1]}"] = natives
    # add qubit characterization section
    return {
        "native_gates": native_gates,
        "characterization": {"single_qubit": {q: qubit.characterization for q, qubit in qubits.items()}},
    }
