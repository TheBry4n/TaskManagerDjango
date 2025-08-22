# Django Task Manager

Un sistema completo di gestione task con funzionalità avanzate per il monitoraggio automatico delle scadenze e riattivazione delle task fallite.

## 🚀 Caratteristiche Principali

- **Gestione Task Completa**: Creazione, modifica, completamento e eliminazione di task
- **Monitoraggio Automatico Scadenze**: Le task scadute vengono automaticamente spostate nella sezione "Failed"
- **Sistema di Riattivazione**: Possibilità di riattivare task fallite con una nuova data di scadenza
- **Interfaccia Utente Moderna**: Design responsive con Bootstrap 5
- **Architettura Repository Pattern**: Separazione pulita tra logica di business e accesso ai dati
- **Gestione Timezone**: Supporto completo per fusi orari locali (Europe/Rome)
- **Sistema di Autenticazione**: Login, registrazione e profili utente
- **API REST**: Endpoint per aggiornamenti automatici dello stato

## 📋 Prerequisiti

- Python 3.8+
- pip (gestore pacchetti Python)
- Git (per clonare il repository)

## 🛠️ Installazione

### 1. Clona il Repository
```bash
git clone <url-del-repository>
cd test_django
```

### 2. Crea e Attiva l'Ambiente Virtuale
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installa le Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configura il Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crea un Superuser (Opzionale)
```bash
python manage.py createsuperuser
```

### 6. Avvia il Server di Sviluppo
```bash
python manage.py runserver
```

Il server sarà disponibile all'indirizzo: http://127.0.0.1:8000/

## 🏗️ Struttura del Progetto

```
test_django/
├── accounts/                 # App per gestione utenti
│   ├── models.py            # Modelli utente
│   ├── views.py             # Viste per autenticazione
│   └── urls.py              # URL per accounts
├── tasks/                   # App principale per gestione task
│   ├── models.py            # Modello Task
│   ├── views.py             # Viste per CRUD task
│   ├── forms.py             # Form per task
│   ├── repository.py        # Pattern Repository per accesso dati
│   ├── core/
│   │   └── base_repository.py  # Repository base generico
│   └── management/
│       └── commands/
│           └── update_overdue_tasks.py  # Comando per aggiornare task scadute
├── templates/               # Template HTML
│   ├── base/
│   ├── accounts/
│   └── tasks/
├── static/                  # File statici (CSS, JS)
└── myproject/              # Configurazione Django
    ├── settings.py
    └── urls.py
```

## 🎯 Modello Task

Il modello `Task` include:

- **Campi Base**: `title`, `description`, `due_date`, `created_at`
- **Stato**: `active`, `completed`, `failed`
- **Proprietà Calcolate**:
  - `is_overdue`: Verifica se la task è scaduta
  - `days_until_due`: Giorni rimanenti alla scadenza
  - `overdue_days`: Giorni di ritardo (per task scadute)
- **Tracciamento**: `reactivation_count` per contare le riattivazioni

## 🔧 Funzionalità Principali

### 1. Gestione Automatica Scadenze
Le task vengono automaticamente controllate e aggiornate:
- **All'apertura della pagina**: Viene chiamato `ensure_overdue_tasks_are_failed()`
- **Alla creazione**: Se una task viene creata già scaduta, viene immediatamente marcata come "failed"
- **Comando manuale**: `python manage.py update_overdue_tasks`

### 2. Sistema di Riattivazione
Le task fallite possono essere riattivate:
- Form dedicato nella pagina di dettaglio
- Validazione della nuova data (deve essere nel futuro)
- Incremento automatico del contatore di riattivazioni

### 3. Pattern Repository
Implementazione del pattern Repository per:
- Separazione della logica di business
- Facilità di testing
- Riutilizzo del codice

## 🧪 Testing

### Test Automatici
```bash
# Esegui tutti i test
python manage.py test

# Test specifici per l'app tasks
python manage.py test tasks

# Test con output verboso
python manage.py test tasks --verbosity=2
```

### Test Manuali

#### 1. Test Funzionalità Scadenze
```bash
# Crea una task scaduta per test
python manage.py shell
```

```python
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from django.contrib.auth.models import User

# Crea un utente di test
user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')

# Crea una task scaduta (ieri)
yesterday = timezone.now() - timedelta(days=1)
task = Task.objects.create(
    title="Task di Test Scaduta",
    description="Questa task è scaduta ieri",
    due_date=yesterday,
    user=user,
    status="active"
)

print(f"Task creata: {task.title}")
print(f"Stato: {task.status}")
print(f"È scaduta: {task.is_overdue}")
print(f"Giorni di ritardo: {task.overdue_days}")
```

#### 2. Test Comando Aggiornamento
```bash
# Esegui il comando per aggiornare task scadute
python manage.py update_overdue_tasks

# Con output verboso
python manage.py update_overdue_tasks --verbosity=2
```

#### 3. Test Interfaccia Web
1. Avvia il server: `python manage.py runserver`
2. Vai su http://127.0.0.1:8000/
3. Registra un nuovo account
4. Crea alcune task con date diverse (passate, presenti, future)
5. Verifica che le task scadute si spostino automaticamente nella sezione "Failed"
6. Prova a riattivare una task fallita

## 🔄 Comandi di Gestione

### Aggiornamento Task Scadute
```bash
python manage.py update_overdue_tasks
```

### Creazione Superuser
```bash
python manage.py createsuperuser
```

### Backup Database
```bash
python manage.py dumpdata > backup.json
```

### Restore Database
```bash
python manage.py loaddata backup.json
```

## 🌍 Configurazione Timezone

Il progetto è configurato per il fuso orario `Europe/Rome`. Per cambiare:

1. Modifica `TIME_ZONE` in `myproject/settings.py`
2. Riavvia il server

## 📱 API Endpoints

- `GET /tasks/api/status/`: Restituisce statistiche task in formato JSON
- `POST /tasks/<id>/complete/`: Completa una task
- `POST /tasks/<id>/reactivate/`: Riattiva una task fallita

## 🎨 Personalizzazione

### Stili CSS
I file CSS sono in `static/css/`:
- `base.css`: Stili generali
- `accounts.css`: Stili per autenticazione
- `tasks.css`: Stili specifici per task

### Template
I template sono organizzati in:
- `templates/base/`: Template base
- `templates/accounts/`: Template per autenticazione
- `templates/tasks/`: Template per gestione task

## 🚨 Risoluzione Problemi

### Task non si aggiornano automaticamente
1. Verifica che il timezone sia configurato correttamente
2. Controlla che `ensure_overdue_tasks_are_failed()` venga chiamato
3. Verifica i log del server per errori

### Errori di Form
1. Verifica che tutti i campi obbligatori siano compilati
2. Controlla che le date siano nel formato corretto
3. Assicurati che la nuova data di riattivazione sia nel futuro

### Problemi di Timezone
1. Verifica `TIME_ZONE` in `settings.py`
2. Controlla che `USE_TZ = True`
3. Riavvia il server dopo modifiche

## 📝 Note di Sviluppo

- Il progetto usa il pattern Repository per l'accesso ai dati
- Le task scadute vengono gestite automaticamente
- L'interfaccia è responsive e moderna
- Il codice è ben documentato e testabile

## 🤝 Contribuire

1. Fork il progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit le modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 👨‍💻 Autore

Creato da [TheBry4n](https://github.com/TheBry4n) come progetto di esempio per dimostrare le best practices di Django con pattern Repository e gestione automatica delle scadenze.

---

**Buon coding! 🚀**
