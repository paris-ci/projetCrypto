from collections import Counter

from tqdm import trange


def verification_globale(message):
    return "Joël" in message


def rotated_letter(letter, key):
    """Rotates a given letter by a given number.

    letter: str

    key: int

    Returns: str
    """

    c = ord(letter)
    cak = c + key
    cakASCII = cak % 255
    char = chr(cakASCII)

    return char


class Dechiffreur:
    def __init__(self, file):
        try:
            with open(file, "r") as f:
                self.message_chiffre = f.read()
        except FileNotFoundError:
            self.message_chiffre = str(file)
        except OSError:
            self.message_chiffre = str(file)

    def dechiffrer(self) -> str:
        pass

    def verifier(self, dechiffre) -> bool:
        return verification_globale(dechiffre)


class Scytale(Dechiffreur):

    def __init__(self, file, lettres_par_colonne=6):
        super().__init__(file)

        # Parametres
        self.lettres_par_colonne = lettres_par_colonne

    def dechiffrer(self) -> str:
        # https://github.com/loganwangtz/Implementation-of-some-simple-Cryptography-methods/blob/master/encrypt.py#L134

        dechiffre = []

        for depart in range(self.lettres_par_colonne):
            for indice in range(depart, len(self.message_chiffre), self.lettres_par_colonne):
                indice_module = indice % len(self.message_chiffre)
                lettre = self.message_chiffre[indice_module]
                dechiffre.append(lettre)

        return ''.join(dechiffre)

        colonne = len(self.message_chiffre) // self.lettres_par_colonne + 1
        return ''.join(
            [self.message_chiffre[i::colonne]
             for i in range(colonne)])

    # def verifier(self, dechiffre) -> bool:
    #    return dechiffre.lower().startswith("fonctionnement")


class Caesar(Dechiffreur):
    def __init__(self, file, intervalle=-7):
        super().__init__(file)

        # Parametres
        self.intervalle = intervalle

    def dechiffrer(self):
        dechiffre = []

        # for char in self.message_chiffre:
        #    dechiffre.append(chr(ord(char) + self.intervalle))
        for letter in self.message_chiffre:
            new_letter = rotated_letter(letter, self.intervalle)
            dechiffre.append(new_letter)

        return "".join(dechiffre)

    # def verifier(self, dechiffre):
    #    return "bravo ! vous" in dechiffre.lower() or "félicitations. mais avouons" in dechiffre.lower()


class CaesarBizzare(Dechiffreur):
    def __init__(self, file, intervalle_pair=6, intervalle_impair=6):
        super().__init__(file)

        # Parametres
        self.intervalle_pair = intervalle_pair
        self.intervalle_impair = intervalle_impair

    def dechiffrer(self):
        dechiffre = []

        # for char in self.message_chiffre:
        #    dechiffre.append(chr(ord(char) + self.intervalle))
        for i, letter in enumerate(self.message_chiffre):
            new_letter = rotated_letter(letter, self.intervalle_pair if i % 2 == 0 else self.intervalle_impair)
            dechiffre.append(new_letter)

        return "".join(dechiffre)

    # def verifier(self, dechiffre):
    #    return "bravo ! vous" in dechiffre.lower() or "félicitations. mais avouons" in dechiffre.lower()


class Vigenere(Dechiffreur):
    def __init__(self, file, cle=None):
        super().__init__(file)

        # Parametres
        if cle is None:
            cle = [2, 9, 3, 2]
        self.cle = cle

    def dechiffrer(self):
        dechiffre = []

        # for char in self.message_chiffre:
        #    dechiffre.append(chr(ord(char) + self.intervalle))
        for i, letter in enumerate(self.message_chiffre):
            indice_cle_actuelle = i % len(self.cle)
            cle_actuelle = self.cle[indice_cle_actuelle]

            new_letter = rotated_letter(letter, cle_actuelle)
            dechiffre.append(new_letter)

        return "".join(dechiffre)


def bruteforcer(Classe, message, min_, max_, argument, **kwargs):
    for i in trange(min_, max_):
        args = {argument: i, **kwargs}

        m = Classe(message, **args)

        md = m.dechiffrer()

        if m.verifier(md):
            return args

    print("Pas de résultat trouvé :(")


def message_info(message):
    try:
        with open(message, "r") as f:
            message_chiffre = f.read()
    except FileNotFoundError:
        message_chiffre = str(message)
    except OSError:
        message_chiffre = str(message)

    analyse_frequentielle(message_chiffre)
    trouver_cle(message_chiffre)


def analyse_frequentielle(message_chiffre):
    print("\nAnalyse fréquentielle du message: ")

    """
      (32) -> 189
    e (101) -> 145
    s (115) -> 88
    i (105) -> 81
    n (110) -> 81
    t (116) -> 74
    r (114) -> 66
    u (117) -> 66
    a (97) -> 57
    o (111) -> 50
    """

    counter = Counter(message_chiffre)

    for lettre, count in counter.most_common(10):
        print(f"{lettre} ({ord(lettre)}) -> {count}")


def trouver_cle(message_chiffre):
    print("\nRecherche de clé ASCII par signature connue")
    print("* Début (Bravo!)")
    bravo_en_clair = "Bravo! "
    bravo_chiffre = message_chiffre[:len(bravo_en_clair)]
    assert len(bravo_chiffre) == len(bravo_en_clair)

    for lettre_chiffree, lettre_en_clair in zip(bravo_chiffre, bravo_en_clair):
        decalage = ord(lettre_chiffree) - ord(lettre_en_clair)

        print(f"{repr(lettre_chiffree)}->{repr(lettre_en_clair)}\t : {decalage}")

    print("* Fin (-- Joël)")
    joel_en_clair = "--\nJoël"
    joel_chiffre = message_chiffre[-len(joel_en_clair):]

    assert len(joel_chiffre) == len(joel_en_clair)

    # Equation de la forme lettre_chiffree - décalage = lettre_en_clair <=> décalage = lettre_chiffree - lettre_en_clair

    for lettre_chiffree, lettre_en_clair in zip(joel_chiffre, joel_en_clair):
        decalage = ord(lettre_chiffree) - ord(lettre_en_clair)

        print(f"{repr(lettre_chiffree)}->{repr(lettre_en_clair)}\t : {decalage}")


if __name__ == "__main__":

    # ** Message 1 ** #

    # m1 = Scytale('m sgsromseeenea ct', lettres_par_colonne=6)
    # m1 = Scytale('message1.txt', lettres_par_colonne=1532)
    # print(bruteforcer(Scytale, m1.dechiffrer(), max_=10000, argument="lettres_par_colonne"))
    # print(m1.dechiffrer())

    # ** Message 2 ** #
    # m2 = Caesar("message2.txt", intervalle=-7) # Works!
    # print(m2.verifier(m2.dechiffrer()))
    # print(m2.dechiffrer())

    # ** Message 3 ** #
    # m3 = Caesar("message3.txt", intervalle=-293) # Works!
    # print(m3.verifier(m3.dechiffrer()))
    # print(m3.dechiffrer())

    # ** Message 4 ** #
    # m4 = CaesarBizzare("message4.txt", intervalle_impair=-45, intervalle_pair=-23) # Works!
    # print(m4.verifier(m4.dechiffrer()))
    # print(m4.dechiffrer())
    # Ou alors
    # m4 = Vigenere("message4.txt", cle=[-23, -45])  # Works!
    # print(m4.dechiffrer())

    # print(bruteforcer(CaesarBizzare, 'message4.txt', min_=-1024, max_=1025, argument="intervalle_impair", intervalle_pair=-23))

    # print(bruteforcer(Caesar, 'message5.txt', min_=-0, max_=10, argument="intervalle"))
    print("Self-Test")
    messages = [
        Scytale('message1.txt', lettres_par_colonne=1532),  # 1
        Caesar("message2.txt", intervalle=-7),  # 2
        Caesar("message3.txt", intervalle=-38),  # 3
        Vigenere("message4.txt", cle=[-23, -45]),  # 4
        Vigenere("message5.txt", cle=[-2, -9, -3]),  # 5
    ]

    for i, message in enumerate(messages):
        print(f"M{i + 1} -> {message.verifier(message.dechiffrer())}")

    m6 = Vigenere("message6.txt", cle=[-7, -2, -9, -11, -10, -4, -3])
    print(m6.dechiffrer())

    message_info("message6.txt")
