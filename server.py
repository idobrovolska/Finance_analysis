import os
import sys
from urllib.parse import parse_qs
from main import process_request


def application(environ, start_response):
    # Перевірка, чи правильно працює сервер
    sys.stdout.write("🔍 Сервер працює\n")
    sys.stdout.flush()

    path = environ.get("PATH_INFO", "/")

    # Обробка статичних файлів (зокрема, графіків у charts/)
    if path.startswith("/charts/"):
        file_path = "." + path
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                data = f.read()
            start_response("200 OK", [("Content-Type", "image/png")])
            return [data]
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"File not found"]

    # Якщо запит без параметрів - віддаємо форму
    if path == "/":
        try:
            with open("form.html", "r", encoding="utf-8") as f:
                html = f.read()
        except FileNotFoundError:
            html = "<h1>⚠️ Форма не знайдена. Створіть файл form.html у каталозі проекту.</h1>"
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        return [html.encode("utf-8")]

    # Якщо GET із параметрами (stock, start_date, end_date, prediction) - обробляємо запит
    if environ["REQUEST_METHOD"] == "GET":
        query_string = environ.get("QUERY_STRING", "")
        sys.stdout.write(f"🔍 Отримано QUERY_STRING: {query_string}\n")
        sys.stdout.flush()

        params = parse_qs(query_string)

        # Додаткова перевірка параметрів
        for key, value in params.items():
            sys.stdout.write(f"🔍 Параметр: {key} = {value}\n")
            sys.stdout.flush()

        if all(k in params for k in ("stock", "start_date", "end_date", "prediction")):
            sys.stdout.write("✅ Усі необхідні параметри присутні\n")
            sys.stdout.flush()

            response_body = process_request(params)
            start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
            return [response_body.encode("utf-8")]
        else:
            sys.stdout.write("⚠️ Не всі параметри присутні\n")
            sys.stdout.flush()

    # Якщо жодне з умов не спрацювало
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Page not found"]
