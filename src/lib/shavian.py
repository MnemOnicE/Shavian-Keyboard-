import logging
import re

import eng_to_ipa as ipa

# Configure logging for ShavianConverter
logger = logging.getLogger("ShavianConverter")
logger.setLevel(logging.WARNING)
# Avoid adding multiple handlers if re-imported
if not logger.handlers:
    # We want to log to a file specifically for unknown characters
    # Use a file handler. We'll put it in the current working directory or
    # logs folder if available.
    # Given the context, writing to 'unknown_ipa_chars.log' in the root
    # is acceptable as per request.
    file_handler = logging.FileHandler("unknown_ipa_chars.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # noqa: E501
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class ShavianConverter:
    def __init__(self, fallback_threshold=0.5):
        self.fallback_threshold = fallback_threshold
        # Mapping based on standard IPA to Shavian correspondence
        self.ipa_map = {
            # Consonants
            'p': '𐑐', 'b': '𐑚',
            't': '𐑑', 'd': '𐑛',
            'k': '𐑒', 'g': '𐑜',
            'f': '𐑓', 'v': '𐑝',
            'θ': '𐑔', 'ð': '𐑞',
            's': '𐑕', 'z': '𐑟',
            'ʃ': '𐑖', 'ʒ': '𐑠',
            'ʧ': '𐑗', 'tʃ': '𐑗', 'ʤ': '𐑡', 'dʒ': '𐑡',
            'j': '𐑘', 'w': '𐑢',
            'ŋ': '𐑙', 'h': '𐑣',

            # Liquids / Nasals
            'l': '𐑤', 'r': '𐑮',
            'm': '𐑥', 'n': '𐑯',

            # Vowels (Short)
            'ɪ': '𐑦',
            # approximate:
            'i': '𐑦',
            'ɛ': '𐑧',
            'e': '𐑧',
            'æ': '𐑨',
            'ə': '𐑩',
            'ʌ': '𐑳',
            'ɒ': '𐑪',
            'ʊ': '𐑫',

            # Vowels (Long/Diphthongs)
            'iː': '𐑰',
            'eɪ': '𐑱',
            'aɪ': '𐑲',
            'ɔɪ': '𐑶',
            'juː': '𐑿',
            'ju': '𐑿',
            'oʊ': '𐑴', 'əʊ': '𐑴',
            'aʊ': '𐑬',
            'uː': '𐑵', 'u': '𐑵',
            'ɔː': '𐑷', 'ɔ': '𐑷',
            'ɑː': '𐑭', 'ɑ': '𐑭',

            # R-colored vowels (approximations)
            'ɑːr': '𐑸', 'ɑr': '𐑸', 'ar': '𐑸',
            'ɔːr': '𐑹', 'ɔr': '𐑹', 'or': '𐑹',
            'ɛər': '𐑺', 'ɛr': '𐑺', 'er': '𐑺',  # air / err distinction is
            'ɜːr': '𐑻', 'ɜr': '𐑻', 'ɝ': '𐑻',
            'ər': '𐑼', 'ɚ': '𐑼',
            'ɪər': '𐑽', 'ɪr': '𐑽',
            'jʊər': '𐑿',  # cure - close enough to yew?

            # Common words (Single letters)
            # These are handled by whole-word lookup if possible, but IPA
            # mapping helps too
        }

        # Common word overrides (ReadLex standard)
        self.word_map = {
            "the": "𐑞",
            "of": "𐑝",
            "and": "𐑯",
            "to": "𐑑",
            "for": "𐑓",
            "a": "𐑩",
        }

    def convert_word(self, word):
        word_lower = word.lower()
        if word_lower in self.word_map:
            return self.word_map[word_lower]

        ipa_text = ipa.convert(word_lower)

        if "*" in ipa_text:
            return word  # Fallback if unknown

        # Remove stress markers
        ipa_text = ipa_text.replace("ˈ", "").replace("ˌ", "")

        shavian_chars = []
        unknown_count = 0
        total_ipa_chars = 0
        i = 0
        while i < len(ipa_text):
            # Try to match 3 chars, then 2, then 1 (greedy match)
            match = None
            for length in [3, 2, 1]:
                if i + length <= len(ipa_text):
                    sub = ipa_text[i:i+length]
                    if sub in self.ipa_map:
                        match = self.ipa_map[sub]
                        shavian_chars.append(match)
                        i += length
                        break

            if match:
                pass  # Already handled
            else:
                # If character not found, count as unknown
                char = ipa_text[i]
                unknown_count += 1
                logger.warning(f"Unknown IPA character '{char}' in word '{word}' (IPA: {ipa_text})")  # noqa: E501

                # Keep it as per Option B (unless threshold exceeded later)
                shavian_chars.append(char)
                i += 1

            # We count 'total chars' as the number of 'units' processed
            # from IPA.
            # If we matched 3 IPA chars to 1 Shavian, is that 1 unit or 3?
            # Usually fallback ratio should be based on input length or
            # output validity.
            pass

        total_ipa_chars = len(ipa_text)

        if total_ipa_chars > 0:
            unknown_ratio = unknown_count / total_ipa_chars
            if unknown_ratio > self.fallback_threshold:
                logger.warning(f"Fallback triggered for '{word}': {unknown_count}/{total_ipa_chars} unknown ({unknown_ratio:.2f} > {self.fallback_threshold})")  # noqa: E501
                return word

        return "".join(shavian_chars)

    def convert_sentence(self, text):
        # Regex to split text into words and separators.
        # Captures words consisting of alphanumeric characters and
        # internal apostrophes/smart quotes.
        # This preserves all whitespace and punctuation as separate tokens.
        parts = re.split(r"([a-zA-Z0-9]+(?:['’][a-zA-Z0-9]+)*)", text)
        converted = []

        # re.split with capturing group returns [sep, match, sep, match, ...]
        # Iterate through all parts
        for part in parts:
            if not part:
                continue

            # check if part matches our word definition
            if re.match(r"^[a-zA-Z0-9]+(?:['’][a-zA-Z0-9]+)*$", part):
                converted.append(self.convert_word(part))
            else:
                # separator/punctuation/whitespace - keep as is
                converted.append(part)

        return "".join(converted)


if __name__ == "__main__":
    converter = ShavianConverter()
    print(converter.convert_sentence("Hello world, this is a test."))
