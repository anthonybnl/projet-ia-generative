# MAGIR

## Implémentation technique

1. Calcul du score

Score par compétence : en première approche la moyene

On calcule la moyenne des scores de chaque compétence pour chaque métier en utilisant la formule suivante :

$$
SC_i= \frac{\sum_{j} SC_j}{N}
$$

En seconde approche : le max

$$SC_i= \max_{j} SC_j$$


Avec $SC_i$ le score de la compétence $i$ et $Niveau_i$ le niveau de maîtrise de la compétence $i$, nous avons calculé le score global de chaque métier en utilisant la formule suivante :

$$
Metier = \frac{\sum_{i} Niveau_i * SC_i}{\sum_{i} Niveau_i}
$$

Egalement, le score pour chaque bloc est :

$$
Bloc = \frac{\sum_{i} Niveau_i * SC_i}{\sum_{i} Niveau_i} \text{ pour les compétences du bloc}
$$