# start frontend

requirements: Node.js online downloaden (npm wird dann automatisch heruntergeladen)

1. in das directory "frontend" gehen (cd frontend)
2. npm install
    hierbei werden alle wichtigen frontend packages heruntergeladen
3. npm start
    damit startet man standardmäßig den host auf "http://localhost:3000/"

# start backend

requirements: Python online herunterladen

1. in "backend" navigieren (cd backend)
2. python -m venv .venv
    venv erstellen worin man packages installiert
3. in "riskchain" navigieren (cd riskchain)
4. manage.py kann jetzt zum steuern benutzt werden
    starten: python manage.py runserver
        -> startet server, jetzt kann man auf
        "http://localhost:8000/admin" gehen um das admin panel zu sehen
        "http://localhost:8000/supplychains/supplychain" hier sieht man die api abfrage und man sieht alle supplychains
        "http://localhost:8000/supplychains/supplychain/1/" heir sieht man die erste supplychain (man kann die 1 auch mit zwei tauschen etc, das ist die id die man auhc bei allen supplychains sieht)
    superuser erstellen: python manage.py createsuperuser
        -> dann terminal befolgen (email kann man weg lassen)
        diese daten am besten merken die brauchst du auch um dich ins adminpanel "http://localhost:8000/admin" ein zu loggen


# updaten requirements.txt

pip freeze > requirements.txt

# Codequalität garantieren

pylint datei.py

oder

pylint [ordner]

# Start AI-Agent Orchestrator with shell

from agents.orchestrator_agent import process_node_with_supervisor
from supplychains.models import Node
node1 = Node.objects.all()[22]
chunks = process_node_with_supervisor(node1)

# benutzen der API Keys

im ordner wo manage.py liegt eine .env datei erstellen (also im riskchain ordner)

from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

dadurch bekommt man key aus .env
dann muss man nur noch in der .env die API keys eintragen
das benutzt man da die API keys Geheim sind und man die dadurch nicht im code verlauf hat
(sonst kann ejder in der History von commits beispielseise den KEY sehen)