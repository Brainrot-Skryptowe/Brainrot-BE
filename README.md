# Reels project


## 🛠️ Setup

1) Create environment

```
python -m venv venv
# this line might be slightly different depending on the shell
./venv/Scripts/activate
```
2) Install packages
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3) Run server
```
uvicorn app.main:app
```
Or if you want to restart server every time python code is changed
```
uvicorn app.main:app --reload
```

4) Include .env file

Please ask developers for the file!

## Before pushing
Type in you shell
```
black . --line-length 80
isort .
ruff format . --line-length 80
```