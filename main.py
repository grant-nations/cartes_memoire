#!/usr/bin/python3

import os
import re
import argparse
import random
from datetime import datetime, timezone

METADATA_FILENAME = "meta.csv"
PAQUETS_DIRNAME = "paquets"
CYAN = "\033[0;36m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0m"
BOLD_WHITE = "\033[1;37m"
OVERRIDE = "outrepasser"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def read_metadata(filepath: str) -> list[tuple[str, str]]:
    """
    Metadata is list of paquet filenames separated by a newline.
    """
    try:
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        lines = []

    # The second element will be a date string formatted as yyyy-mm-dd hh:mm
    paquets = []
    for l in lines:
        p = l.split(",")
        if len(p) < 2:
            p.append("")  # Correct for packets missing timestamp
        paquets.append(p)

    return paquets


def get_datetime_str() -> str:
    return datetime.now(timezone.utc).strftime(DATETIME_FORMAT)


def write_metadata(filepath: str, paquets_queue: list[tuple[str, str]]) -> None:
    with open(filepath, "w") as f:
        f.writelines([",".join(p) + "\n" for p in paquets_queue])


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


def update_paquets_queue(paquet_queue: list[tuple[str, str]], root_path: str) -> None:
    paquet_name_to_queue_entry = {p[0]: p for p in paquets_queue}
    paquet_names_set = set(paquet_name_to_queue_entry.keys())
    all_packet_names_set = set()

    paquets_dirpath = os.path.join(root_path, PAQUETS_DIRNAME)

    for file_or_dir in os.listdir(paquets_dirpath):
        if os.path.isfile(os.path.join(paquets_dirpath, file_or_dir)):
            all_packet_names_set.add(file_or_dir)

    new_paquet_names_set = all_packet_names_set - paquet_names_set
    for new_paquet_name in new_paquet_names_set:
        paquet_queue.append((new_paquet_name, get_datetime_str()))

    paquets_to_rm_set = paquet_names_set - all_packet_names_set
    for paquet_name_to_rm in paquets_to_rm_set:
        paquets_queue.remove(paquet_name_to_queue_entry[paquet_name_to_rm])


def get_index_by_paquet_name(paquets_queue: list[tuple[str, str]], paquet_name: str) -> int:
    for i, p in enumerate(paquets_queue):
        if p[0] == paquet_name:
            return i

    raise ValueError


def gender_ambiguous(answer: str) -> bool:
    pattern = r"(l'.*?(\s|$))|(les\s)"

    return re.search(pattern, answer) is not None


def wait_for_enter() -> None:
    while True:
        if input("Appuie sur Enter pour continuer.") == "":
            break


def wait_for_correct_answer(answer: str) -> bool:
    """
    Waits for return; returns True if answer is overridden as true via `OVERRIDE`.
    """
    while True:
        _input = input(f"Tape {CYAN}{answer}{RESET} pour continuer: ").strip().lower()
        if _input == OVERRIDE:
            return True
        elif _input == answer:
            return False


def clear_terminal() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run_exercise(paquet_filename: str, root_path: str) -> None:
    paquet_name = paquet_filename.replace("_", " ").replace(".csv", "").capitalize()
    print(f"{BOLD_WHITE}{paquet_name}{RESET}")
    wait_for_enter()

    clear_terminal()
    paquet_filepath = os.path.join(root_path, PAQUETS_DIRNAME, paquet_filename)

    prompts_answers_genders = read_paquet(paquet_filepath)
    random.shuffle(prompts_answers_genders)

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
            message = f"{YELLOW}Incorrect{RESET}. Bonne réponse: {CYAN}{answer}{RESET}"

            if gender is not None:
                message += f"{CYAN} ({gender}.) {RESET}"

            print(message)
            override = wait_for_correct_answer(answer)
            if not override:
                prompts_answers_genders.insert(0, (prompt, answer, gender))

        clear_terminal()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-q", "--queue", action="store_true", help="Jeter un coup d'œuil à la queue"
    )
    parser.add_argument("-p", "--paquet", help="Choisir le paquet à réviser.")

    return parser.parse_args()


if __name__ == "__main__":

    root = os.path.dirname(__file__)
    metadata_path = os.path.join(root, METADATA_FILENAME)

    paquets_queue: list[tuple[str, str]] = read_metadata(metadata_path)
    old_len = len(paquets_queue)

    update_paquets_queue(paquets_queue, root)
    new_len = len(paquets_queue)

    if new_len - old_len != 0:
        write_metadata(metadata_path, paquets_queue)

    if len(paquets_queue) == 0:
        print("Aucun paquet trouvé ; il n'y a rien à faire.")
        exit(0)

    args = parse_args()

    if args.queue:
        print("Queue:")
        for paquet in paquets_queue[:-1]:
            paquet_str = f"  - {paquet[0]}"
            if paquet[1] != "":
                paquet_str += f" {GREEN}({paquet[1]}){RESET}"
            print(paquet_str)

        final_paquet_str = f"  - {paquets_queue[-1][0]}"
        if paquets_queue[-1][1] != "":
            final_paquet_str += f" {GREEN}({paquets_queue[-1][1]}){RESET}"
        final_paquet_str += f" {CYAN}<-- On est là{RESET}"
        print(final_paquet_str)
        exit(0)

    index_to_pop = -1
    if args.paquet:
        try:
            index_to_pop = get_index_by_paquet_name(paquets_queue, args.paquet)
        except ValueError:
            print(f"{YELLOW}ATTENTION:{RESET} Paquet {args.paquet} introuvable")
            exit(1)

    paquet_name, paquet_date = paquets_queue.pop(index_to_pop)

    run_exercise(paquet_name, root)

    paquets_queue.insert(0, (paquet_name, get_datetime_str()))
    write_metadata(metadata_path, paquets_queue)
