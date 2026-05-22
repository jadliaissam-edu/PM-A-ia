from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json, re, subprocess, io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

TASKS = ["Conception", "Développement", "Tests", "Déploiement"]
MAPPING = {
    "conception": "Conception", 
    "développement": "Développement", "developpement": "Développement",
    "tests": "Tests", "test": "Tests", 
    "déploiement": "Déploiement", "deploiement": "Déploiement"
}
def run_model(prompt):
    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2", prompt],
            capture_output=True, text=True, timeout=25
        )
        return result.stdout.strip()
    except Exception as e:
        return ""

@csrf_exempt
def assistant(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non supportée"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    mode = data.get("mode", "").lower()
    text = data.get("text", "").strip()

    if not text:
        return JsonResponse({"error": "Le champ 'text' est obligatoire"}, status=400)

    # ---------------- CHAT ----------------
    if mode == "chat":
        reply = run_model(text)
        clean_reply = re.sub(r'[^a-zA-Z0-9À-ÿ\s.,!?\'"\-_() ]', '', reply)
        return JsonResponse({"reply": clean_reply.strip() or "Je n'ai pas pu générer de réponse."})

    # ---------------- REPORT ----------------
    elif mode == "report":
        prompt = f"Rédige un rapport structuré pour le sujet: {text}"
        report = run_model(prompt)
        clean_report = re.sub(r'[^a-zA-Z0-9À-ÿ\s.,!?\'"\-_()\n]', '', report)
        return JsonResponse({"report": clean_report.strip() or "Impossible de générer le rapport."})

    # ---------------- GANTT ----------------
    elif mode == "gantt":
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.barh("Conception", 5, left=0, color="#3498db", edgecolor="black")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)
        plt.close(fig)
        return HttpResponse(buf.read(), content_type="image/png")

    # ---------------- ANALYTICS ----------------
    elif mode == "analytics":
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie([25,25,25,25], labels=TASKS, autopct='%1.1f%%')
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150)
        buf.seek(0)
        plt.close(fig)
        return HttpResponse(buf.read(), content_type="image/png")

    return JsonResponse({"error": "Mode invalide"}, status=400)
