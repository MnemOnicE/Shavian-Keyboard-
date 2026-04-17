import os
import sys

# import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))
from lib.shavian import ShavianConverter  # noqa: E402


def test_convert_word_simple():
    converter = ShavianConverter()
    # Simple word check
    # "the" is mapped to "𐑞"
    assert converter.convert_word("the") == "𐑞"
    # "test" -> t ɛ s t -> 𐑑 𐑧 𐑕 𐑑
    assert converter.convert_word("test") == "𐑑𐑧𐑕𐑑"


def test_convert_sentence():
    converter = ShavianConverter()
    # "Hello world"
    # Hello -> hɛloʊ -> 𐑣 𐑧 𐑤 𐑴 (approx)
    # world -> w ɜr l d -> 𐑢 𐑻 𐑤 𐑛 (approx)
    result = converter.convert_sentence("Hello world")
    # We check parts because exact IPA mapping can vary
    assert "𐑣" in result  # h
    assert "𐑢" in result  # w

    # Check punctuation preservation
    text = "Hello, world!"
    result = converter.convert_sentence(text)
    assert "," in result
    assert "!" in result
    assert " " in result


def test_fallback():
    converter = ShavianConverter()
    # A made up word that eng-to-ipa won't know well or returns stars
    # eng-to-ipa returns "word*" if unknown or sometimes just best guess.
    # If it returns * it triggers fallback in convert_word if * is in ipa_text

    # Let's try a very weird string that shouldn't match anything
    weird = "xyz123"
    # eng-to-ipa probably returns "xyz123*" or similar
    # The converter should return original text
    assert converter.convert_word(weird) == weird


def test_casing_preservation_in_sentence():
    # The converter currently converts words to lowercase before lookup/conversion.  # noqa: E501
    # The output is Shavian characters which don't have casing (unicameral).
    # But punctuation and whitespace should be preserved.
    converter = ShavianConverter()
    text = "Hello... World?"
    res = converter.convert_sentence(text)
    assert "..." in res
    assert "?" in res
