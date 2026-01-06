import eng_to_ipa as ipa

words = ["hello", "world", "this", "is", "a", "test", "shavian", "phonetic", "alphabet"]
for word in words:
    print(f"{word}: {ipa.convert(word)}")
