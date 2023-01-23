import numpy as np
from scipy import signal


class ExecutionResult:
    """Container returned by :meth:`qibolab.platforms.platform.Platform.execute_pulse_sequence`.

    Args:
        i_values (np.ndarray): Measured I values obtained from the experiment.
        q_values (np.ndarray): Measured Q values obtained from the experiment.
    """

    # TODO: Distinguish cases where we have single shots vs averaged values

    def __init__(self, i_values, q_values, shots=None):
        self.I = i_values
        self.Q = q_values
        self.shots = shots
        self.in_progress = False

    @property
    def MSR(self):
        return np.sqrt(self.I**2 + self.Q**2)

    @property
    def phase(self):
        phase = np.angle(self.I + 1j * self.Q)
        return signal.detrend(np.unwrap(phase))

    @property
    def probability(self):
        return np.sum(self.shots) / len(self.shots)

    def to_dict(self):
        return {
            "MSR[V]": self.MSR.ravel(),
            "i[V]": self.I.ravel(),
            "q[V]": self.Q.ravel(),
            "phase[rad]": self.phase.ravel(),
        }

    def __len__(self):
        return np.prod(self.I.shape)
