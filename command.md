##### common system commands
# pip3 freeze > requirements.txt
pip3 install flask flask-sqlalchemy flask-security-too
# source .env/bin/activate
# python3 -m venv .env
# pip3 install -r requirements.txt
# sudo systemctl stop redis
# $ celery -A app.celery worker --loglevel INFO

# frontend commands
# npm create vue@latest
# cd frontend
# npm install
# npm run dev

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