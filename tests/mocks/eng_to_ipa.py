def convert(text):
    # Very basic mock that returns some IPA-like string for common words
    # to allow tests to pass if they don't mock it themselves.
    if text.lower() == "test":
        return "tɛst"
    if text.lower() == "hello":
        return "hɛloʊ"
    if text.lower() == "world":
        return "wɜːrld"
    return text + "*"
