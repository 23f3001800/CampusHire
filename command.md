##### common system commands
# pip3 freeze > requirements.txt
pip3 install flask flask-sqlalchemy flask-security-too
# source venv/bin/activate
# python3 -m venv venv
# pip3 install -r requirements.txt
# sudo systemctl stop redis
# $ celery -A app.celery worker --loglevel INFO

# frontend commands
# npm create vue@latest
# cd frontend
# npm install
# npm run dev

### initalise datbase
python3 -m scripts.init_db
## seed dummy data in database
python3 -m scripts.seed_data

#### git tracking file commands
# git init
git add . or filename
rm -rf directory_name
git commit -m "Milestone1"
git push -u origin main
git branch
# This keeps both your local commits and the remote ones.
git push -u origin main
# If you want your local repo to replace everything on GitHub
git push origin main --force
# Fetch remote changes:
git fetch origin
# Rebase remote commits on top of your work:
git pull origin main --rebase


### redis server

 pip install celery redis flask-mail
 redis-server

 sudo systemctl stop redis
 sudo systemctl start redis && redis-cli ping   

celery -A celery_config.celery_app worker --loglevel=info
celery -A celery_config.celery_app beat --loglevel=info
celery -A celery_worker worker --loglevel=info
celery -A celery_worker.celery beat --loglevel=info --dry-run



python trigger_tasks.py --ping
python trigger_tasks.py --async

### database initalization 

python -m scripts.init_db
python -m scripts.seed_data


python3 -c "
from app import app
rules = [str(r) for r in app.url_map.iter_rules() if 'offer' in str(r).lower()]
print('\n'.join(rules) or 'No offer routes found')
"

from tasks import generate_monthly_report, generate_company_monthly_reports
generate_monthly_report.delay()
generate_company_monthly_reports.delay()





## how to run the application 
for backend and frontend

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

cd frontend
npm install
npm run dev