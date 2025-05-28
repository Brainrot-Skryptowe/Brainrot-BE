# Reels project

## 🛠️ Setup

1) Create a virtual environment

```
python -m venv venv
# this line might be slightly different depending on your shell
./venv/Scripts/activate
```

2) Install packages
```
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3) Install FFmpeg  
[Download FFmpeg](https://www.gyan.dev/ffmpeg/builds/)

4) Install pre-commit
```
pre-commit install
```

5) Run the server
```
uvicorn app.main:app
```
Or, if you want the server to restart every time Python code is changed:
```
uvicorn app.main:app --reload
```

6) Include the .env file

Please ask the developers for this file!

## Before pushing and committing changes

Remember to install pre-commit:
```
pre-commit install
```

Try to commit changes using the naming convention:
```
git add .
git commit -m "fix: fix something"
```

If your commit was not successful, run:
```
ruff check . --fix
```