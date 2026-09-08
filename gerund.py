# -*- coding: utf-8 -*-
"""Turn a Pokemon name into an English present participle (gerund)."""
import re, unicodedata

VOWELS = set("aeiou")
DOUBLING = set("bdglmnprt")
# unstressed / schwa-ish final syllables: doubling here sounds wrong (Aggron -> Aggroning)
WEAK_TAIL = ("on","en","in","an","er","ar","or","el","al","il","ol","ul",
             "um","us","om","ur","ir","yr","ow","ey","em","im")

# Names where the rules produce something silly; curated by hand.
OVERRIDES = {
    "Nidoran♀": "Nidoran-Fing",
    "Nidoran♂": "Nidoran-Ming",
    "Mr. Mime":  "Mr. Miming",
    "Mr. Rime":  "Mr. Riming",
    "Mime Jr.":  "Miming Jr.",
    "Type: Null":"Type-Nulling",
    "Porygon2":  "Porygon2ing",
    "Porygon-Z": "Porygon-Zing",
}

def _syllables(w):
    return max(1, len(re.findall(r"[aeiouy]+", w.lower())))

def _inflect_word(w):
    lw = w.lower()
    if lw.endswith("ie"):                       # Alcremie -> Alcremying
        return w[:-2] + "ying"
    if lw.endswith("e") and not lw.endswith(("ee","oe","ye","ae","ue")) \
       and len(w) > 2 and lw[-2] not in VOWELS:  # Kricketune -> Kricketuning
        return w[:-1] + "ing"
    if lw.endswith("c") and len(lw) > 1 and lw[-2] in VOWELS:
        return w + "king"                       # Togetic -> Togeticking
    if (len(lw) >= 3 and lw[-1] in DOUBLING and lw[-2] in VOWELS
            and lw[-3] not in VOWELS and _syllables(lw) <= 2
            and not lw.endswith(WEAK_TAIL)):     # Zubat -> Zubatting
        return w + w[-1] + "ing"
    return w + "ing"                            # Mew -> Mewing

def gerund(name):
    if name in OVERRIDES:
        return OVERRIDES[name]
    n = name.replace("’", "'")             # Farfetch’d -> Farfetch'd
    parts = n.split(" ")
    parts[-1] = _inflect_word(parts[-1])        # inflect only the head word
    return " ".join(parts)

if __name__ == "__main__":
    for t in ["Mew","Charizard","Zubat","Mudkip","Aggron","Eevee","Alcremie",
              "Kricketune","Sunkern","Great Tusk","Tapu Koko","Farfetch’d",
              "Ho-Oh","Flabébé","Chi-Yu","Iron Jugulis","Pikachu","Mr. Mime"]:
        print(("%-14s -> %s" % (t, gerund(t))).encode("ascii","backslashreplace").decode())
