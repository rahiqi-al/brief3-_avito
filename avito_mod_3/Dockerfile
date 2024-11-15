from python:3.10.12

WORKDIR /AVITO_MOD_3

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
