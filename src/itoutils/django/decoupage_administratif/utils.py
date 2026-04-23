from unidecode import unidecode


def normalize_string_for_search(str):
    return unidecode(str).upper().replace("-", " ").replace("’", "'").rstrip()


def code_insee_to_code_dept(code_insee):
    return code_insee[:3] if code_insee.startswith("97") else code_insee[:2]
