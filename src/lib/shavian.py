import eng_to_ipa as ipa
import re

class ShavianConverter:
    def __init__(self):
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
            'ɪ': '𐑦', 'i': '𐑦', # approximate
            'ɛ': '𐑧', 'e': '𐑧',
            'æ': '𐑨',
            'ə': '𐑩',
            'ʌ': '𐑳',
            'ɒ': '𐑪',
            'ʊ': '𐑫',

            # Vowels (Long/Diphthongs)
            'iː': '𐑰', 'i': '𐑰', # Context dependent, usually final i is 𐑦 or 𐑰
            'eɪ': '𐑱',
            'aɪ': '𐑲',
            'ɔɪ': '𐑶',
            'juː': '𐑿', 'ju': '𐑿',
            'oʊ': '𐑴', 'əʊ': '𐑴',
            'aʊ': '𐑬',
            'uː': '𐑵', 'u': '𐑵',
            'ɔː': '𐑷', 'ɔ': '𐑷',
            'ɑː': '𐑭', 'ɑ': '𐑭',

            # R-colored vowels (approximations)
            'ɑːr': '𐑸', 'ɑr': '𐑸', 'ar': '𐑸',
            'ɔːr': '𐑹', 'ɔr': '𐑹', 'or': '𐑹',
            'ɛər': '𐑺', 'ɛr': '𐑺', 'er': '𐑺', # air / err distinction is subtle in some IPA
            'ɜːr': '𐑻', 'ɜr': '𐑻', 'ɝ': '𐑻',
            'ər': '𐑼', 'ɚ': '𐑼',
            'ɪər': '𐑽', 'ɪr': '𐑽',
            'jʊər': '𐑿', # cure - close enough to yew?

            # Common words (Single letters)
            # These are handled by whole-word lookup if possible, but IPA mapping helps too
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
            return word # Fallback if unknown

        # Remove stress markers
        ipa_text = ipa_text.replace("ˈ", "").replace("ˌ", "")

        shavian_chars = []
        i = 0
        while i < len(ipa_text):
            # Try to match 3 chars, then 2, then 1 (greedy match)
            match = None
            for length in [3, 2, 1]:
                if i + length <= len(ipa_text):
                    sub = ipa_text[i:i+length]
                    if sub in self.ipa_map:
                        match = self.ipa_map[sub]
                        i += length
                        break

            if match:
                shavian_chars.append(match)
            else:
                # If character not found, keep it (e.g. punctuation?)
                # or just skip. For now, let's keep it to debug
                shavian_chars.append(ipa_text[i])
                i += 1

        return "".join(shavian_chars)

    def convert_sentence(self, text):
        # Simple tokenization by space, preserving punctuation could be improved
        # For now, just split by space
        words = text.split(" ")
        converted = []
        for w in words:
            # Strip punctuation for conversion, then re-attach?
            # Ideally use a regex tokenizer.
            # Minimal viable:
            clean_word = re.sub(r'[^\w\s]', '', w)
            punctuation = w[len(clean_word):] if len(clean_word) < len(w) else ""
            prefix = w[:len(w)-len(clean_word)-len(punctuation)] if len(clean_word) < len(w) else "" # logic slightly flawed if prefix exists

            # Better:
            match = re.match(r"([^\w]*)([\w']+)([^\w]*)", w)
            if match:
                pre, core, post = match.groups()
                conv = self.convert_word(core)
                converted.append(pre + conv + post)
            else:
                converted.append(w)

        return " ".join(converted)

if __name__ == "__main__":
    converter = ShavianConverter()
    print(converter.convert_sentence("Hello world, this is a test."))
