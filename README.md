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