import random

fichier_entree = "le_bonheur_et_le_malheur_1.csv"
fichier_sortie = "output.txt"

# Lire toutes les lignes
with open(fichier_entree, "r", encoding="utf-8") as f:
    lignes = f.readlines()

# Mélanger les lignes
random.shuffle(lignes)

# Écrire les lignes mélangées
with open(fichier_sortie, "w", encoding="utf-8") as f:
    f.writelines(lignes)

print(f"{len(lignes)} lignes mélangées et écrites dans {fichier_sortie}")
