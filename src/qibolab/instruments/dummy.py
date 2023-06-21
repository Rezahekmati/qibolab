from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
from qibo.config import log

from qibolab import AcquisitionType, AveragingMode, ExecutionParameters
from qibolab.instruments.abstract import Controller
from qibolab.instruments.port import Port
from qibolab.platform import Qubit
from qibolab.pulses import PulseSequence
from qibolab.qubits import QubitId
from qibolab.sweeper import Sweeper


@dataclass
class DummyPort(Port):
    name: str
    offset: float = 0.0
    lo_frequency: int = 0
    lo_power: int = 0
    gain: int = 0
    attenuation: int = 0
    power_range: int = 0
    filters: Optional[dict] = None


class DummyInstrument(Controller):
    """Dummy instrument that returns random voltage values.

    Useful for testing code without requiring access to hardware.

    Args:
        name (str): name of the instrument.
        address (int): address to connect to the instrument.
            Not used since the instrument is dummy, it only
            exists to keep the same interface with other
            instruments.
    """

    PortType = DummyPort
    sampling_rate = 1

    def connect(self):
        log.info("Connecting to dummy instrument.")

    def setup(self, *args, **kwargs):
        log.info("Setting up dummy instrument.")

    def start(self):
        log.info("Starting dummy instrument.")

    def stop(self):
        log.info("Stopping dummy instrument.")

    def disconnect(self):
        log.info("Disconnecting dummy instrument.")

    def get_values(self, options, sequence, shape):
        results = {}
        for ro_pulse in sequence.ro_pulses:
            if options.acquisition_type is AcquisitionType.DISCRIMINATION:
                if options.averaging_mode is AveragingMode.SINGLESHOT:
                    values = np.random.randint(2, size=shape)
                elif options.averaging_mode is AveragingMode.CYCLIC:
                    values = np.random.rand(*shape)
            elif options.acquisition_type is AcquisitionType.RAW:
                samples = int(ro_pulse.duration * self.sampling_rate)
                waveform_shape = tuple(samples * dim for dim in shape)
                values = np.random.rand(*waveform_shape) * 100 + 1j * np.random.rand(*waveform_shape) * 100
            elif options.acquisition_type is AcquisitionType.INTEGRATION:
                values = np.random.rand(*shape) * 100 + 1j * np.random.rand(*shape) * 100
            results[ro_pulse.qubit] = results[ro_pulse.serial] = options.results_type(values)
        return results

    def play(self, qubits: Dict[QubitId, Qubit], sequence: PulseSequence, options: ExecutionParameters):
        exp_points = 1 if options.averaging_mode is AveragingMode.CYCLIC else options.nshots
        shape = (exp_points,)
        return self.get_values(options, sequence, shape)

    def sweep(
        self,
        qubits: Dict[QubitId, Qubit],
        sequence: PulseSequence,
        options: ExecutionParameters,
        *sweepers: List[Sweeper],
    ):
        if options.averaging_mode is not AveragingMode.CYCLIC:
            nshots = (options.nshots,)
            shape = nshots + tuple(len(sweeper.values) for sweeper in sweepers)
        else:
            shape = tuple(len(sweeper.values) for sweeper in sweepers)
        return self.get_values(options, sequence, shape)
