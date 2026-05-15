from flask import Flask, request, jsonify, send_file
import subprocess
import re
import matplotlib
# Force Matplotlib à ne pas chercher d'interface graphique (indispensable sur serveur)
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Liste stricte des phases du projet
TASKS = ["Conception", "Développement", "Tests", "Déploiement"]

# Dictionnaire pour normaliser les retours textuels de Llama 3.2
MAPPING = {
    "conception": "Conception", 
    "développement": "Développement", "developpement": "Développement",
    "tests": "Tests", "test": "Tests", 
    "déploiement": "Déploiement", "deploiement": "Déploiement"
}

def run_model(prompt):
    """Exécute Llama 3.2 via Ollama de manière sécurisée avec un timeout."""
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True, text=True, timeout=25
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("Timeout expiré pour Ollama.")
        return ""
    except Exception as e:
        print(f"Erreur Ollama: {e}")
        return ""

@app.route("/assistant", methods=["POST"])
def assistant():
    data = request.get_json() or {}
    mode = data.get("mode", "").lower()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Le champ 'text' est obligatoire"}), 400

    # ---------------- CHAT ----------------
    if mode == "chat":
        reply = run_model(text)
        # Nettoyage souple pour garder une vraie phrase de discussion
        clean_reply = re.sub(r'[^a-zA-Z0-9À-ÿ\s.,!?\'"\-_() ]', '', reply)
        return jsonify({"reply": clean_reply.strip() or "Je n'ai pas pu générer de réponse."})

    # ---------------- GANTT ----------------
    elif mode == "gantt":
        prompt = (
            f"Sujet de projet: {text}. Évalue une durée réaliste pour ces 4 tâches de manière séquentielle. "
            f"Répond UNIQUEMENT sous ce format strict, une tâche par ligne, sans texte explicatif avant ou après:\n"
            f"Conception: X jours\nDéveloppement: X jours\nTests: X jours\nDéploiement: X jours"
        )
        prediction = run_model(prompt)

        # Valeurs par défaut logiques (20 jours au total) si le modèle échoue ou prend trop de temps
        parsed_tasks = {t: {"name": t, "start": 0, "duration": 5} for t in TASKS}
        
        for line in prediction.splitlines():
            # Capture le nom de la tâche, le chiffre et l'unité (jours/semaines/mois)
            match = re.search(r'([\wÀ-ÿ\s]+):\s*(\d+)\s*(jours|semaines|mois|jour|semaine)', line, re.IGNORECASE)
            if match:
                raw_name = match.group(1).lower().strip()
                value = int(match.group(2))
                unit = match.group(3).lower()
                
                task_name = next((MAPPING[k] for k in MAPPING if k in raw_name), None)
                if task_name:
                    # Conversion automatique en jours pour l'affichage de l'axe
                    if "semaine" in unit:
                        duration = value * 7
                    elif "mois" in unit:
                        duration = value * 30
                    else:
                        duration = value
                    parsed_tasks[task_name]["duration"] = max(1, duration)

        # Calcul de la chronologie (chaque tâche commence là où la précédente s'arrête)
        tasks_list = []
        current_start = 0
        for t in TASKS:
            task_data = parsed_tasks[t]
            task_data["start"] = current_start
            tasks_list.append(task_data)
            current_start += task_data["duration"]

        # Création du graphique Gantt
        fig, ax = plt.subplots(figsize=(10, 4))
        for task in tasks_list:
            ax.barh(task["name"], task["duration"], left=task["start"], color="#3498db", edgecolor="black")
        
        ax.set_xlabel("Temps cumulé (Jours)")
        ax.set_title(f"Planning Gantt - {text}")
        ax.invert_yaxis()  # Met la Conception tout en haut
        plt.tight_layout()

        # Sauvegarde en mémoire du graphique
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)
        plt.close(fig)  # LIBÈRE LA RAM DU SERVEUR IMMEDIATEMENT
        return send_file(buf, mimetype="image/png")

    # ---------------- ANALYTICS ----------------
    elif mode == "analytics":
        prompt = (
            f"Sujet: {text}. Donne une répartition en % logique pour le budget de temps entre: "
            f"Conception, Développement, Tests, Déploiement. "
            f"La somme doit faire exactement 100. Répond UNIQUEMENT sous ce format strict:\n"
            f"Conception: X\nDéveloppement: X\nTests: X\nDéploiement: X"
        )
        prediction = run_model(prompt)

        # Répartition équitable par défaut (25% partout) en cas de bug du modèle
        parsed_sizes = {t: 25 for t in TASKS}
        
        for line in prediction.splitlines():
            match = re.search(r'([\wÀ-ÿ\s]+):\s*(\d+)', line)
            if match:
                raw_name = match.group(1).lower().strip()
                value = int(match.group(2))
                
                task_name = next((MAPPING[k] for k in MAPPING if k in raw_name), None)
                if task_name:
                    parsed_sizes[task_name] = value

        sizes = list(parsed_sizes.values())
        
        # Sécurité Python : On force la somme à faire strictement 100% quoi qu'il arrive
        total = sum(sizes) if sum(sizes) > 0 else 100
        sizes = [round(v * 100 / total) for v in sizes]
        sizes[0] += (100 - sum(sizes))  # Corrige les erreurs d'arrondis sur la première case

        # Génération du graphique en Camembert (Pie Chart)
        fig, ax = plt.subplots(figsize=(6, 6))
        colors = ['#2ecc71', '#3498db', '#e67e22', '#95a5a6']
        ax.pie(sizes, labels=TASKS, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops={'edgecolor':'black'})
        ax.set_title(f"Répartition analytique des ressources - {text}")
        plt.tight_layout()

        # Sauvegarde et envoi
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)
        plt.close(fig)  # LIBÈRE LA RAM DU SERVEUR IMMEDIATEMENT
        return send_file(buf, mimetype="image/png")

    # ---------------- REPORT ----------------
    elif mode == "report":
        prompt = (
            f"Rédige un rapport de projet structuré, court et professionnel en 4 sections claires "
            f"(Conception, Développement, Tests, Déploiement) pour le sujet suivant : '{text}'."
        )
        report = run_model(prompt)
        # Nettoyage qui préserve la ponctuation française, les retours à la ligne (\n) et les tirets
        clean_report = re.sub(r'[^a-zA-Z0-9À-ÿ\s.,!?\'"\-_()\n]', '', report)
        return jsonify({"report": clean_report.strip() or "Impossible de générer le rapport."})

    else:
        return jsonify({"error": "Mode de traitement invalide. Options: chat, gantt, analytics, report"}), 400

if __name__ == "__main__":
    # Tourne sur le port 8080. debug=False est obligatoire pour éviter d'instancier deux fois le modèle en RAM
    app.run(host="0.0.0.0", port=8080, debug=False)
