import numpy as np
import pytest

from qibolab.instruments.abstract import Instrument
from qibolab.instruments.qblox.cluster import Cluster, Cluster_Settings
from qibolab.instruments.qblox.cluster_qrm_rf import (
    ClusterQRM_RF,
    ClusterQRM_RF_Settings,
)
from qibolab.instruments.qblox.port import (
    ClusterRF_OutputPort,
    ClusterRF_OutputPort_Settings,
    QbloxInputPort,
    QbloxInputPort_Settings,
)
from qibolab.pulses import DrivePulse, PulseSequence, ReadoutPulse
from qibolab.sweeper import Parameter, Sweeper, SweeperType

CLUSTER_NAME = "cluster"
CLUSTER_ADDRESS = "192.168.0.6"

MODULE_NAME = "qrm_rf"
MODULE_ADDRESS = "192.168.0.6:10"
OUTPUT_CHANNEL = "L3-25_a"
INPUT_CHANNEL = "L2-5_a"
ATTENUATION = 38
LO_FREQUENCY = 7_000_000_000
GAIN = 0.6
TIME_OF_FLIGHT = 500
ACQUISITION_DURATION = 900


@pytest.fixture(scope="module")
def cluster():
    cluster = Cluster(CLUSTER_NAME, CLUSTER_ADDRESS, Cluster_Settings())
    return cluster


@pytest.fixture(scope="module")
def qrm_rf():
    settings = ClusterQRM_RF_Settings(
        {
            "o1": ClusterRF_OutputPort_Settings(
                channel=OUTPUT_CHANNEL,
                attenuation=ATTENUATION,
                lo_frequency=LO_FREQUENCY,
                gain=GAIN,
            ),
            "i1": QbloxInputPort_Settings(
                channel=INPUT_CHANNEL,
                acquisition_hold_off=TIME_OF_FLIGHT,
                acquisition_duration=ACQUISITION_DURATION,
            ),
        }
    )
    qrm_rf = ClusterQRM_RF(MODULE_NAME, MODULE_ADDRESS, settings)
    return qrm_rf


@pytest.fixture(scope="module")
def connected_qrm_rf(cluster: Cluster, qrm_rf: ClusterQRM_RF):
    cluster.connect()
    qrm_rf.connect(cluster.device)
    qrm_rf.setup()
    yield qrm_rf
    qrm_rf.disconnect()
    cluster.disconnect()


def test_ClusterQRM_RF_Settings():
    # Test default value
    qrm_rf_settings = ClusterQRM_RF_Settings()
    for port in ["o1", "i1"]:
        assert port in qrm_rf_settings.ports


def test_instrument_interface(qrm_rf: ClusterQRM_RF):
    # Test compliance with :class:`qibolab.instruments.abstract.Instrument` interface
    for abstract_method in Instrument.__abstractmethods__:
        assert hasattr(qrm_rf, abstract_method)

    for attribute in ["name", "address", "is_connected", "signature", "tmp_folder", "data_folder"]:
        assert hasattr(qrm_rf, attribute)


def test_init(qrm_rf: ClusterQRM_RF):
    assert qrm_rf.name == MODULE_NAME
    assert qrm_rf.address == MODULE_ADDRESS
    assert type(qrm_rf.settings.ports["o1"]) == ClusterRF_OutputPort_Settings
    assert type(qrm_rf.settings.ports["i1"]) == QbloxInputPort_Settings
    assert qrm_rf.device == None
    for port in ["o1", "i1"]:
        assert port in qrm_rf.ports
    output_port: ClusterRF_OutputPort = qrm_rf.ports["o1"]
    assert output_port.sequencer_number == 0
    input_port: QbloxInputPort = qrm_rf.ports["i1"]
    assert input_port.input_sequencer_number == 0
    assert input_port.output_sequencer_number == 0


@pytest.mark.qpu
def test_connect(cluster: Cluster, qrm_rf: ClusterQRM_RF):
    cluster.connect()
    qrm_rf.connect(cluster.device)
    assert qrm_rf.is_connected
    assert not qrm_rf is None
    # test configuration after connection
    assert qrm_rf.device.get("in0_att") == 0
    assert qrm_rf.device.get("out0_offset_path0") == 0
    assert qrm_rf.device.get("out0_offset_path1") == 0
    assert qrm_rf.device.get("scope_acq_avg_mode_en_path0") == True
    assert qrm_rf.device.get("scope_acq_avg_mode_en_path1") == True
    assert qrm_rf.device.get("scope_acq_sequencer_select") == qrm_rf.DEFAULT_SEQUENCERS["i1"]
    assert qrm_rf.device.get("scope_acq_trigger_level_path0") == 0
    assert qrm_rf.device.get("scope_acq_trigger_level_path1") == 0
    assert qrm_rf.device.get("scope_acq_trigger_mode_path0") == "sequencer"
    assert qrm_rf.device.get("scope_acq_trigger_mode_path1") == "sequencer"

    default_sequencer = qrm_rf.device.sequencers[qrm_rf.DEFAULT_SEQUENCERS["o1"]]
    assert default_sequencer.get("channel_map_path0_out0_en") == True
    assert default_sequencer.get("channel_map_path1_out1_en") == True
    assert default_sequencer.get("cont_mode_en_awg_path0") == False
    assert default_sequencer.get("cont_mode_en_awg_path1") == False
    assert default_sequencer.get("cont_mode_waveform_idx_awg_path0") == 0
    assert default_sequencer.get("cont_mode_waveform_idx_awg_path1") == 0
    assert default_sequencer.get("marker_ovr_en") == True
    assert default_sequencer.get("marker_ovr_value") == 15
    assert default_sequencer.get("mixer_corr_gain_ratio") == 1
    assert default_sequencer.get("mixer_corr_phase_offset_degree") == 0
    assert default_sequencer.get("offset_awg_path0") == 0
    assert default_sequencer.get("offset_awg_path1") == 0
    assert default_sequencer.get("sync_en") == False
    assert default_sequencer.get("upsample_rate_awg_path0") == 0
    assert default_sequencer.get("upsample_rate_awg_path1") == 0

    _device_num_sequencers = len(qrm_rf.device.sequencers)
    for s in range(1, _device_num_sequencers):
        assert qrm_rf.device.sequencers[s].get("channel_map_path0_out0_en") == False
        assert qrm_rf.device.sequencers[s].get("channel_map_path1_out1_en") == False

    qrm_rf.disconnect()
    cluster.disconnect()


@pytest.mark.qpu
def test_setup(cluster: Cluster, qrm_rf: ClusterQRM_RF):
    cluster.connect()
    qrm_rf.connect(cluster.device)
    qrm_rf.setup()

    assert qrm_rf.ports["o1"].channel == OUTPUT_CHANNEL
    assert qrm_rf.device.get("out0_att") == ATTENUATION
    assert qrm_rf.device.get("out0_in0_lo_en") == True
    assert qrm_rf.device.get("out0_in0_lo_freq") == LO_FREQUENCY
    assert qrm_rf.device.get("out0_in0_lo_freq") == LO_FREQUENCY
    import math

    default_sequencer = qrm_rf.device.sequencers[qrm_rf.DEFAULT_SEQUENCERS["o1"]]
    assert math.isclose(default_sequencer.get("gain_awg_path0"), GAIN, rel_tol=1e-4)
    assert math.isclose(default_sequencer.get("gain_awg_path1"), GAIN, rel_tol=1e-4)

    assert default_sequencer.get("mod_en_awg") == True

    assert qrm_rf.ports["o1"].nco_freq == 0
    assert qrm_rf.ports["o1"].nco_phase_offs == 0

    assert qrm_rf.ports["i1"].channel == INPUT_CHANNEL
    assert default_sequencer.get("demod_en_acq") == True

    assert qrm_rf.ports["i1"].acquisition_hold_off == TIME_OF_FLIGHT
    assert qrm_rf.ports["i1"].acquisition_duration == ACQUISITION_DURATION

    qrm_rf.disconnect()
    cluster.disconnect()


@pytest.mark.qpu
def test_pulse_sequence(connected_qrm_rf: ClusterQRM_RF, dummy_qrc):
    ps = PulseSequence()
    for channel in connected_qrm_rf.channels:
        ps.add(DrivePulse(0, 200, 1, 6.8e9, np.pi / 2, "Gaussian(5)", channel))
        ps.add(ReadoutPulse(200, 2000, 1, 7.1e9, np.pi / 2, "Rectangular()", channel, qubit=0))
        ps.add(ReadoutPulse(200, 2000, 1, 7.2e9, np.pi / 2, "Rectangular()", channel, qubit=1))
    from qibolab import create_platform

    platform = create_platform("qblox")
    qubits = platform.qubits
    connected_qrm_rf.ports["i1"].hardware_demod_en = True
    connected_qrm_rf.process_pulse_sequence(qubits, ps, 1000, 1, 10000)
    connected_qrm_rf.upload()
    connected_qrm_rf.play_sequence()
    results = connected_qrm_rf.acquire()
    connected_qrm_rf.ports["i1"].hardware_demod_en = False
    connected_qrm_rf.process_pulse_sequence(qubits, ps, 1000, 1, 10000)
    connected_qrm_rf.upload()
    connected_qrm_rf.play_sequence()
    results = connected_qrm_rf.acquire()


@pytest.mark.qpu
def test_sweepers(connected_qrm_rf: ClusterQRM_RF, dummy_qrc):
    ps = PulseSequence()
    qd_pulses = {}
    ro_pulses = {}
    for channel in connected_qrm_rf.channels:
        qd_pulses[0] = DrivePulse(0, 200, 1, 7e9, np.pi / 2, "Gaussian(5)", channel, qubit=0)
        ro_pulses[0] = ReadoutPulse(200, 2000, 1, 7.1e9, np.pi / 2, "Rectangular()", channel, qubit=0)
        ro_pulses[1] = ReadoutPulse(200, 2000, 1, 7.2e9, np.pi / 2, "Rectangular()", channel, qubit=1)
        ps.add(qd_pulses[0], ro_pulses[0], ro_pulses[1])
    from qibolab import create_platform

    platform = create_platform("qblox")
    qubits = platform.qubits

    freq_width = 300e6 * 2
    freq_step = freq_width // 100

    delta_frequency_range = np.arange(-freq_width // 2, freq_width // 2, freq_step)
    sweeper = Sweeper(
        Parameter.frequency,
        delta_frequency_range,
        pulses=ro_pulses,
        type=SweeperType.OFFSET,
    )

    connected_qrm_rf.process_pulse_sequence(qubits, ps, 1000, 1, 10000, sweepers=[sweeper])
    connected_qrm_rf.upload()
    connected_qrm_rf.play_sequence()
    results = connected_qrm_rf.acquire()

    delta_duration_range = np.arange(0, 140, 1)
    sweeper = Sweeper(
        Parameter.duration,
        delta_duration_range,
        pulses=qd_pulses,
        type=SweeperType.ABSOLUTE,
    )

    connected_qrm_rf.process_pulse_sequence(qubits, ps, 1000, 1, 10000, sweepers=[sweeper])
    connected_qrm_rf.upload()
    connected_qrm_rf.play_sequence()
    results = connected_qrm_rf.acquire()


def test_process_acquisition_results():
    pass


@pytest.mark.qpu
def test_start_stop(connected_qrm_rf: ClusterQRM_RF):
    connected_qrm_rf.start()
    connected_qrm_rf.stop()
    # check all sequencers are stopped and all offsets = 0


@pytest.mark.qpu
def test_disconnect(cluster: Cluster, qrm_rf: ClusterQRM_RF):
    cluster.connect()
    qrm_rf.connect(cluster.device)
    qrm_rf.disconnect()
    assert qrm_rf.is_connected == False
    cluster.disconnect()
