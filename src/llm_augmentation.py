import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.environ.get("GEMINI_API_KEY")

model = None
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")


async def augmenter_textes_batch(textes: list[str]) -> list[str]:
    """
    Prend une liste entière de textes et effectue un unique appel API (batch)
    pour augmenter tous les textes qui font moins de 5 mots.
    """
    if not textes:
        return []

    # 1. Identifier les textes qui ont besoin d'être augmentés
    textes_courts = {}
    
    for i, texte in enumerate(textes):
        if not texte or not isinstance(texte, str):
            continue
        t = texte.strip()
        # condition métier : moins de 5 mots -> on augmente
        if t and len(t.split()) < 5:
            textes_courts[str(i)] = t

    # S'il n'y a aucun texte trop court, on renvoie la liste d'origine sans faire d'appel API
    if not textes_courts:
        return textes

    if not model:
        print("⚠️ Pas de modèle Gemini disponible pour le batch")
        return textes

    # 2. Préparer le prompt JSON
    prompt = f"""
Tu es un expert en systèmes d'information spécialisé en traitement du langage naturel.
Ta mission est d’enrichir une liste de compétences techniques très courtes pour améliorer leur qualité sémantique dans des embeddings NLP.

Règles STRICTES :
- Produis UNE seule phrase par compétence
- Longueur : entre 12 et 18 mots par phrase
- Pas d’explication, pas de commentaires
- Respect strict du sens initial de la compétence
- Ajoute uniquement du contexte technique pertinent (outils, usage, environnement, objectif)
- Tu dois IMPERATIVEMENT retourner un objet JSON valide où la clé est l'index fourni (string) et la valeur est la phrase enrichie. Ne renvoie AUCUN test markdown en dehors du JSON.

Voici le dictionnaire JSON des textes (index -> texte_court) à enrichir :
{json.dumps(textes_courts, ensure_ascii=False, indent=2)}
"""

    try:
        response = await model.generate_content_async(prompt)

        if not response.text:
            return textes

        texte_brut = response.text.strip()
        
        # Nettoyage automatique du markdown encadrant le dict JSON si le modèle en renvoie
        if texte_brut.startswith('```json'):
            texte_brut = texte_brut[7:]
        elif texte_brut.startswith('```'):
            texte_brut = texte_brut[3:]
            
        if texte_brut.endswith('```'):
            texte_brut = texte_brut[:-3]
            
        texte_brut = texte_brut.strip()

        # 3. Parser et fusionner les réponses au format JSON
        try:
            resultat_json = json.loads(texte_brut)
            
            texte_modifies = list(textes) # copie de la liste initiale
            
            print(f"⭐ [LLM BATCH AUGMENTATION] ({len(textes_courts)} champs augmentés en 1 seul appel) :")
            for idx_str, original_txt in textes_courts.items():
                if idx_str in resultat_json:
                    augmented_txt = resultat_json[idx_str]
                    idx = int(idx_str)
                    texte_modifies[idx] = augmented_txt
                    print(f"  [{idx}] Original: {original_txt} -> Augmenté: {augmented_txt}")
                    
            return texte_modifies
            
        except json.JSONDecodeError as e:
            print("⚠️ Erreur de parsing JSON du modèle :", response.text)
            return textes

    except Exception as e:
        print(f"⚠️ Erreur API LLM lors du batch : {e}")
        return textes