import itertools
import logging
import multiprocessing
from collections import Counter

import coloredlogs
from tqdm import tqdm

logger = logging.getLogger(__name__)
coloredlogs.install(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)

with open("mots_fr.txt", "r") as f:
    COMMON_WORDS = set(f.read().splitlines())


def get_message_score(message: str) -> int:
    score = 0
    for mot in message.split():
        if mot in COMMON_WORDS:
            score += 1

    return score


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


def dechiffre_vignere(message_chiffre, cle, max_len=300) -> str:
    # https://github.com/loganwangtz/Implementation-of-some-simple-Cryptography-methods/blob/master/encrypt.py#L134
    dechiffre = []

    # for char in self.message_chiffre:
    #    dechiffre.append(chr(ord(char) + self.intervalle))
    for i, letter in enumerate(message_chiffre):
        indice_cle_actuelle = i % len(cle)
        cle_actuelle = cle[indice_cle_actuelle]

        new_letter = rotated_letter(letter, cle_actuelle)
        dechiffre.append(new_letter)

        if max_len and i > max_len:
            break

    return "".join(dechiffre)


def bruteforce_vignere(message_chiffre, taille_cle=1) -> tuple:
    BORNE_MIN = -20
    BORNE_MAX = 0

    max_score = 0
    for line in message_chiffre:
        max_score += len(line.split())

    nb_iterations = (abs(BORNE_MIN) + abs(BORNE_MAX)) ** taille_cle

    best_score, best_key, best_message = 0, (0,), ""

    for cle_test in tqdm(itertools.product(range(BORNE_MIN, BORNE_MAX), repeat=taille_cle), desc=f"Vignere bruteforce pour une taille de clé de {taille_cle}", total=nb_iterations):

        message_dechiffre = dechiffre_vignere(message_chiffre, cle_test)
        score = get_message_score(message_dechiffre.lower())

        if score > best_score:
            best_score, best_key, best_message = score, cle_test, message_dechiffre
            logger.debug(f"Meilleur score {score} pour l'instant avec {cle_test}:\n\n{message_dechiffre}")
            if best_score > 4:
                best_message = dechiffre_vignere(message_chiffre, best_key, max_len=0)
                score = get_message_score(best_message.lower())
                if score > 200:
                    break

    # logger.debug(f"Clé testée : {cle_test}")

    best_message = dechiffre_vignere(message_chiffre, best_key, max_len=0)
    best_score = get_message_score(best_message.lower())

    return best_score, best_key, best_message


def main_truebruteforce(message_files=None, correct_score=5):
    if message_files is None:
        message_files = {"message2.txt": (1, 1), "message6.txt": (6, 15)}  # "message3.txt":(1,1), "message4.txt":(2,2), "message5.txt":(3,3),

    for file_name, taille_cle in message_files.items():
        with open(file_name, "r") as f:
            message_chiffre = f.read()

        min_taille_cle, max_taille_cle = taille_cle

        for taille_cle in range(min_taille_cle, max_taille_cle + 1):
            best_score, best_key, best_message = bruteforce_vignere(message_chiffre, taille_cle=taille_cle)
            if best_score > 0:
                logger.info(f"Meilleur score={best_score} sur une clé={best_key} de taille={taille_cle} pour message {file_name}:"
                            f"\n\n{best_message}")

                if best_score > correct_score:
                    logger.info(f"Trouvé message {file_name}")
                    print("\a")
                    with open(file_name + "d", "w") as f:
                        f.write(f"Meilleur score={best_score} sur une clé={best_key} de taille={taille_cle} pour message {file_name}\n" + best_message)
                    break


def get_key_possibilities(part_message_chiffre, essais=2):
    SPACE_CHAR = ord(" ")

    counter = Counter(part_message_chiffre)

    espace_dans = counter.most_common(essais)
    cles_possibles = []
    for cle, compteur in espace_dans:
        cles_possibles.append(SPACE_CHAR - ord(cle))

    return cles_possibles


def bruteforce_vigenere_frequency(message_chiffre, taille_cle=3) -> tuple:
    # Découpage du message
    cles_possibles = []

    for i in range(taille_cle):
        cles_possibles.append(get_key_possibilities(message_chiffre[i::taille_cle]))

    best_score, best_key, best_message = 0, (0,), ""

    for cle_test in tqdm(itertools.product(*cles_possibles)):

        message_dechiffre = dechiffre_vignere(message_chiffre, cle_test)
        score = get_message_score(message_dechiffre.lower())

        if score > best_score:
            best_score, best_key, best_message = score, cle_test, message_dechiffre
            logger.debug(f"Meilleur score {score} pour l'instant avec {cle_test}:\n\n{message_dechiffre}")
            if best_score > 4:
                best_message = dechiffre_vignere(message_chiffre, best_key, max_len=0)
                score = get_message_score(best_message.lower())
                if score > 10:
                    break

    # logger.debug(f"Clé testée : {cle_test}")

    best_message = dechiffre_vignere(message_chiffre, best_key, max_len=0)
    best_score = get_message_score(best_message.lower())

    return best_score, best_key, best_message


def main_frequency_analysis(message_files=None, correct_score=1000):
    bornes =  (1, 15)
    if message_files is None:
        message_files = {"arthur.txt":bornes,}
                         #"antoine.txt": bornes,
                         #"chloe.txt": bornes,
                         #"florian.txt": bornes,
                         #"marine.txt": bornes,
                         #"pascal.txt": (20, 20),
                         #"souhila.txt": bornes}

    for file_name, taille_cle in message_files.items():
        with open(file_name, "r", encoding="utf8") as f:
            message_chiffre = f.read()

        min_taille_cle, max_taille_cle = taille_cle

        for taille_cle in range(min_taille_cle, max_taille_cle + 1):
            best_score, best_key, best_message = bruteforce_vigenere_frequency(message_chiffre, taille_cle=taille_cle)
            if best_score > 0:
                logger.info(f"Meilleur score={best_score} sur une clé={best_key} de taille={taille_cle} pour message {file_name}:"
                            f"\n\n{best_message}")

                if best_score > correct_score:
                    logger.info(f"Trouvé message {file_name}")
                    print("\a")
                    with open(file_name + "d", "w") as f:
                        f.write(f"Meilleur score={best_score} sur une clé={best_key} de taille={taille_cle} pour message {file_name}\n" + best_message)
                    break


main_frequency_analysis()
