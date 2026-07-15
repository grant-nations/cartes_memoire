#!/usr/bin/python3

import os
import re

METADATA_FILENAME = "meta.txt"
PAQUETS_DIRNAME = "paquets"
CYAN = "\033[0;36m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"


def read_metadata(filepath: str) -> list[str]:
    """
    Metadata is list of paquet filenames separated by a newline.
    """
    try:
        with open(filepath, "r") as f:
            paquets = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        paquets = []

    return paquets


def write_metadata(filepath: str, paquets_queue: list[str]) -> None:
    with open(filepath, "w") as f:
        f.writelines([p + "\n" for p in paquets_queue])


def read_paquet(filepath: str) -> list[tuple[str, str, str]]:
    prompts_answers_genders = []

    with open(filepath, "r") as f:
        for line in f.readlines():
            split = line.split(",")
            for i in range(len(split)):
                split[i] = split[i].strip().lower()

            if len(split) < 3:
                split.append(None)

            prompts_answers_genders.append(tuple(split))

    return prompts_answers_genders


def update_paquets_queue(paquet_queue: list[str], root_path: str) -> None:
    paquets_set = set(paquets_queue)
    new_paquets_set = set()

    paquets_dirpath = os.path.join(root_path, PAQUETS_DIRNAME)

    for file_or_dir in os.listdir(paquets_dirpath):
        if os.path.isfile(os.path.join(paquets_dirpath, file_or_dir)):
            new_paquets_set.add(file_or_dir)

    new_paquets_set = new_paquets_set - paquets_set
    for new_paquet in new_paquets_set:
        paquet_queue.append(new_paquet)


def gender_ambiguous(answer: str) -> bool:
    pattern = r"(l'.*?(\s|$))|(les\s)"

    return re.search(pattern, answer) is not None


def wait_for_enter() -> None:
    while True:
        if input("Appuie sur Enter pour continuer.") == "":
            break


def wait_for_correct_answer(answer: str) -> None:
    while True:
        if (
            input(f"Tape {CYAN}{answer}{RESET} pour continuer: ").strip().lower()
            == answer
        ):
            break


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run_exercise(paquet_filename: str, root_path: str) -> None:
    clear_terminal()
    paquet_filepath = os.path.join(root_path, PAQUETS_DIRNAME, paquet_filename)

    prompts_answers_genders = read_paquet(paquet_filepath)

    while len(prompts_answers_genders) > 0:
        remaining = len(prompts_answers_genders)
        prompt, answer, gender = prompts_answers_genders.pop()

        response = input(f"({remaining}) {prompt}: ").strip().lower()

        correct = False
        if response == answer:
            if gender_ambiguous(answer):
                if gender is None:
                    print("ATTENTION: Genre est None quand 'm' ou 'f' était attendu")
                    correct = True
                else:
                    correct = input("Genre (m/f): ").strip().lower() == gender
            else:
                correct = True

        if correct:
            print(f"{CYAN}Correct.{RESET}")
            wait_for_enter()
        else:
            print(f"{YELLOW}Incorrect{RESET}. Bonne réponse: {CYAN}{answer}{RESET}")
            wait_for_correct_answer(answer)
            prompts_answers_genders.insert(0, (prompt, answer, gender))

        clear_terminal()


if __name__ == "__main__":
    root = os.path.dirname(__file__)
    metadata_path = os.path.join(root, METADATA_FILENAME)

    paquets_queue = read_metadata(metadata_path)
    update_paquets_queue(paquets_queue, root)

    if len(paquets_queue) == 0:
        print("Aucun paquet trouvé ; il n'y a rien à faire.")

    paquet = paquets_queue.pop()

    run_exercise(paquet, root)

    paquets_queue.insert(0, paquet)
    write_metadata(metadata_path, paquets_queue)
