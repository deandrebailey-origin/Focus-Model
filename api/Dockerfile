FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1

# dont ccreate pycahche files which are useless
# print logs immediatley instead of buffering them and writing them later
# pip doens;t keep downloaded files

WORKDIR /app
RUN pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY model.py main.py focus_model.pth ./

RUN useradd --create-home appuser

# createes a refualr user and switche to it
# ususlaity container run as root
# security risk

USER appuser


EXPOSE 8000

# run the app with uvicorn

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

  # docker calls your health endpoint call every 30 seconds

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# accept connections from every where
