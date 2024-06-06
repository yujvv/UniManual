import deepl

auth_key = "f63c02c5-f056-..."  # Replace with your key
translator = deepl.Translator(auth_key)

result = translator.translate_text("Hello, world!", target_lang="FR")
print(result.text)  # "Bonjour, le monde !"




# Translate text into a target language, in this case, French:
result = translator.translate_text("Hello, world!", target_lang="FR")
print(result.text)  # "Bonjour, le monde !"

# Translate multiple texts into British English
result = translator.translate_text(
    ["お元気ですか？", "¿Cómo estás?"], target_lang="EN-GB"
)
print(result[0].text)  # "How are you?"
print(result[0].detected_source_lang)  # "JA" the language code for Japanese
print(result[1].text)  # "How are you?"
print(result[1].detected_source_lang)  # "ES" the language code for Spanish

# Translate into German with less and more Formality:
print(
    translator.translate_text(
        "How are you?", target_lang="DE", formality="less"
    )
)  # 'Wie geht es dir?'
print(
    translator.translate_text(
        "How are you?", target_lang="DE", formality="more"
    )
)  # 'Wie geht es Ihnen?'