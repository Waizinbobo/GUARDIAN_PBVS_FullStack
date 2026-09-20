# GUARDIAN (PBVS)

Law-Tech B2B SaaS platform for workforce risk intelligence and evidence-based background verification. The original Stitch HTML pages are retained under `templates/core` and connected to Django routes.

## Included modules

- Django Authentication: register, login, logout and protected dashboard
- Companies, employees, cases, evidence and four-level risk records
- Consent-gated background verification and results
- Public-only blacklist exposure (`is_public=True`)
- Warning/news publishing
- Contact reports and evidence-backed appeals
- Django Admin and authenticated Django REST Framework APIs
- Audit logs for registration, verification, reports and appeals

## Local setup (SQLite quick start)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On macOS/Linux activate with `source .venv/bin/activate`.

## MySQL Workbench CE setup

1. Open `database_setup.sql` in MySQL Workbench and execute it. Change the example password first.
2. Export the values in `.env.example` into your operating-system environment.
3. Set `DB_ENGINE=mysql`, `DB_NAME=guardian_pbvs`, `DB_USER=guardian_user`, and the matching password.
4. Run `python manage.py migrate`, then `python manage.py createsuperuser`.

PowerShell example:

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="guardian_pbvs"
$env:DB_USER="guardian_user"
$env:DB_PASSWORD="your_password"
python manage.py migrate
python manage.py runserver
```

## Main URLs

- Website: `http://127.0.0.1:8000/`
- Account dashboard: `/dashboard/`
- Django Admin: `/admin/`
- REST API root: `/api/`

## Security notes

Use a strong `SECRET_KEY`, set `DEBUG=False`, configure HTTPS and secure cookies before deployment. NRC and evidence are sensitive personal data. Publish a risk record or evidence only after authorization, documented review, notice and appeal procedures. Public pages never expose records unless staff explicitly sets `is_public=True`.

## Tests

```bash
python manage.py test
python manage.py check
```
