FROM python:3.8-alpine

EXPOSE 3111

WORKDIR /app

COPY ./techtrends/requirements.txt .

RUN pip install -r requirements.txt

COPY ./techtrends/ ./

RUN python ./init_db.py

CMD [ "python", "app.py" ]