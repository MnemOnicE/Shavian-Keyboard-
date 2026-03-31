import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Define a mock for numpy array behavior
class MockArray(list):
    def __init__(self, data, dtype=None):
        if isinstance(data, (list, tuple, MockArray)):
            super().__init__(list(data))
        else:
            # Handle scalar-like or single-item init
            super().__init__([data])
        self.dtype = dtype

    def __repr__(self):
        return f"MockArray({super().__repr__()})"

def mock_concatenate(arrays, axis=0):
    # Improved mock_concatenate to handle various sequence types and nested structures
    flat_list = []
    for a in arrays:
        if isinstance(a, (list, tuple, MockArray)):
            flat_list.extend(list(a))
        else:
            flat_list.append(a)
    return MockArray(flat_list)

@pytest.fixture(autouse=True)
def mock_deps():
    # Use patch.dict to safely mock missing modules
    # This prevents side effects on other tests in a shared environment.
    with patch.dict(sys.modules, {
        'webrtcvad': MagicMock(),
        'numpy': MagicMock()
    }):
        import numpy as np
        np.float32 = "float32"
        # Setup the mock for array to use our helper
        np.array.side_effect = lambda data, dtype=None: MockArray(data, dtype)
        np.concatenate.side_effect = mock_concatenate

        # Now import VadManager after mocks are applied
        from backend.vad import VadManager
        yield VadManager

def test_flush_initial_state(mock_deps):
    vm = mock_deps()
    results = vm.flush()
    assert results == []
    assert vm.triggered is False
    assert vm.speech_buffer == []
    assert len(vm.pre_trigger_buffer) == 0
    assert len(vm.buffer) == 0
    assert vm.consecutive_speech == 0
    assert vm.consecutive_silence == 0

def test_flush_triggered_with_speech(mock_deps):
    vm = mock_deps()
    vm.triggered = True
    vm.speech_buffer = [MockArray([1, 2]), MockArray([3, 4])]

    results = vm.flush()

    assert len(results) == 1
    assert results[0] == [1, 2, 3, 4]

    assert vm.triggered is False
    assert vm.speech_buffer == []
    assert len(vm.pre_trigger_buffer) == 0
    assert len(vm.buffer) == 0
    assert vm.consecutive_speech == 0
    assert vm.consecutive_silence == 0

def test_flush_not_triggered_with_speech(mock_deps):
    vm = mock_deps()
    vm.triggered = False
    vm.speech_buffer = [MockArray([1, 2])]
    vm.consecutive_speech = 3

    results = vm.flush()

    assert results == []
    assert vm.triggered is False
    assert vm.speech_buffer == []
    assert vm.consecutive_speech == 0

def test_flush_resets_all_state_variables(mock_deps):
    vm = mock_deps()
    vm.triggered = True
    vm.speech_buffer = [MockArray([1])]
    vm.pre_trigger_buffer.append(MockArray([2]))
    vm.buffer = MockArray([3, 4])
    vm.consecutive_speech = 5
    vm.consecutive_silence = 2

    vm.flush()

    assert vm.triggered is False
    assert vm.speech_buffer == []
    assert len(vm.pre_trigger_buffer) == 0
    assert len(vm.buffer) == 0
    assert vm.consecutive_speech == 0
    assert vm.consecutive_silence == 0
