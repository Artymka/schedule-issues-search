FROM python:3.13
WORKDIR /app

# COPY ./app /app
# COPY ./utils /app
# COPY req.txt /app

COPY ./app/__init__.py app/
COPY ./app/main.py app/
COPY ./app/search_issues.py app/

COPY ./utils/__init__.py utils/
COPY ./utils/lesson.py utils/
COPY ./utils/schedules_issue.py utils/
COPY ./utils/utils.py utils/

COPY req.txt .

EXPOSE 80
RUN pip install --no-cache-dir --upgrade -r req.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD uvicorn app.main:app