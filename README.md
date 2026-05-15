## 🤖 Intégration et Configuration du Modèle IA (Llama 3.2)

L'application utilise **Llama 3.2 (3B)** via **Ollama** pour la génération de rapports, l'analyse de projets et les fonctionnalités de chat. Ce modèle a été choisi pour sa grande précision en langue française et sa faible empreinte en mémoire RAM (~2.2 Go), ce qui le rend idéal pour notre serveur de 8 Go.

### 1. Installation d'Ollama sur le Serveur

Exécutez la commande suivante dans le terminal de votre serveur pour installer Ollama (Linux / Ubuntu) :

```bash
curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh
## Téléchargement et Initialisation du Modèle
ollama run llama3.2
## Déploiement de l'Application Flask
# Activation de l'environnement virtuel (si applicable)
source venv/bin/activate

## Lancement de l'application
python main.py
## Tester sur postman

