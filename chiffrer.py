zwsp = "​"
hidden_in = """Bonjour joël,
Ceci n'est pas le bon message, désolé :(

Bon courage pour trouver le vrai message caché!
-- 
Arthur

PS: Ma signature est plus longue que la votre, mais c'est pas très utile ici"""

hidden_message = """Bravo, ceci est le bon message secret! :)"""

def message_to_ord(message:str):
    return [ord(m) for m in message]


if __name__ == '__main__':
    length = len(hidden_in)
    ords = message_to_ord(hidden_message)
    ords += [0] * (length-len(ords))

    final = []

    for i in range(length):
        final.append(hidden_in[i])
        final.append(zwsp * ords[i])

    with open("message7", "w") as f:
        f.write("".join(final))
