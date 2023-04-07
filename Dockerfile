FROM python:3.11

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD [ "python", "./core.py" ]