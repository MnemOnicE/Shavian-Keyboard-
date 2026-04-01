import os
import sys
import unittest
from unittest.mock import patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from lib.shavian import ShavianConverter  # noqa: E402


class TestShavianFallback(unittest.TestCase):
    def setUp(self):
        # Reset log file before tests if needed, or just let it append
        self.log_file = "unknown_ipa_chars.log"
        # Truncate file instead of removing, to preserve FileHandler's stream
        with open(self.log_file, "w") as f:  # noqa: F841
            pass
        self.converter = ShavianConverter(fallback_threshold=0.5)

    def tearDown(self):
        # Clean up log file? Maybe keep it for inspection
        pass

    @patch("eng_to_ipa.convert")
    def test_no_unknown_chars(self, mock_convert):
        # 'cat' -> 'kæt' (all known)
        # k -> 𐑒, æ -> 𐑨, t -> 𐑑
        mock_convert.return_value = "kæt"
        result = self.converter.convert_word("cat")
        self.assertEqual(result, "𐑒𐑨𐑑")

        # Verify log file is empty/not created for warnings
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as f:
                content = f.read()
                self.assertEqual(content, "")

    @patch("eng_to_ipa.convert")
    def test_unknown_below_threshold(self, mock_convert):
        # 'test' -> 't?st' (1 unknown out of 4 = 25% < 50%)
        # t -> 𐑑, ? -> ?, s -> 𐑕, t -> 𐑑
        mock_convert.return_value = "t?st"
        result = self.converter.convert_word("test")

        # Should return mixed string
        self.assertEqual(result, "𐑑?𐑕𐑑")

        # Verify log file has warning
        self.assertTrue(os.path.exists(self.log_file))
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("Unknown IPA character '?'", content)

    @patch("eng_to_ipa.convert")
    def test_unknown_above_threshold(self, mock_convert):
        # 'weird' -> '????' (100% unknown)
        mock_convert.return_value = "????"
        result = self.converter.convert_word("weird")

        # Should fallback to original word
        self.assertEqual(result, "weird")

        # Verify log file has fallback message
        with open(self.log_file, "r") as f:
            content = f.read()
            self.assertIn("Fallback triggered", content)

    @patch("eng_to_ipa.convert")
    def test_custom_threshold(self, mock_convert):
        # Set strict threshold 10%
        converter = ShavianConverter(fallback_threshold=0.1)

        # 'test' -> 't?st' (25% > 10%)
        mock_convert.return_value = "t?st"
        result = converter.convert_word("test")

        # Should fallback
        self.assertEqual(result, "test")


if __name__ == "__main__":
    unittest.main()
