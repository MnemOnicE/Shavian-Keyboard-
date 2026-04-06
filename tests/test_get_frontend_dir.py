import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Mock all dependencies of backend.main to avoid import issues
# The mock modules must be in sys.modules before importing backend.main
mock_modules = [
    'fastapi',
    'fastapi.middleware.cors',
    'fastapi.staticfiles',
    'faster_whisper',
    'webrtcvad',
    'numpy'
]
for mod in mock_modules:
    sys.modules[mod] = MagicMock()

# Mock local imports
sys.modules['lib.shavian'] = MagicMock()
sys.modules['backend.vad'] = MagicMock()

from backend.main import get_frontend_dir

class TestGetFrontendDir(unittest.TestCase):
    def setUp(self):
        # Save original sys state
        self.original_frozen = getattr(sys, 'frozen', None)
        self.original_meipass = getattr(sys, '_MEIPASS', None)
        self.original_executable = sys.executable

    def tearDown(self):
        # Restore original sys state
        if self.original_frozen is None:
            if hasattr(sys, 'frozen'):
                del sys.frozen
        else:
            sys.frozen = self.original_frozen

        if self.original_meipass is None:
            if hasattr(sys, '_MEIPASS'):
                del sys._MEIPASS
        else:
            sys._MEIPASS = self.original_meipass

        sys.executable = self.original_executable

    def test_dev_mode(self):
        """Test development mode (sys.frozen is false or missing)"""
        if hasattr(sys, 'frozen'):
            del sys.frozen

        # The expected path is relative to the backend/main.py file location
        # backend/main.py is at src/backend/main.py
        # get_frontend_dir returns os.path.join(os.path.dirname(__file__), '..', 'frontend')
        # where __file__ is src/backend/main.py

        import backend.main
        main_file = backend.main.__file__
        expected_dir = os.path.abspath(os.path.join(os.path.dirname(main_file), '..', 'frontend'))

        actual_dir = get_frontend_dir()

        # Normalize paths for comparison
        self.assertEqual(os.path.abspath(actual_dir), expected_dir)

    def test_frozen_with_meipass(self):
        """Test frozen mode with sys._MEIPASS available"""
        sys.frozen = True
        sys._MEIPASS = "/tmp/fake_meipass"

        expected_dir = os.path.join("/tmp/fake_meipass", "frontend")
        actual_dir = get_frontend_dir()

        self.assertEqual(actual_dir, expected_dir)

    def test_frozen_without_meipass(self):
        """Test frozen mode without sys._MEIPASS (uses sys.executable directory)"""
        sys.frozen = True
        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        fake_executable = "/usr/bin/autoshavian"
        sys.executable = fake_executable

        expected_dir = os.path.join("/usr/bin", "frontend")
        actual_dir = get_frontend_dir()

        self.assertEqual(actual_dir, expected_dir)

if __name__ == '__main__':
    unittest.main()
