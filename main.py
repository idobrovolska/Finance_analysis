import os
import json
from urllib.parse import parse_qs
from modules.logger import Logger
from modules.data_collector import DataCollector
from modules.data_processor import DataProcessor
from modules.prediction_evaluator import PredictionEvaluator
from modules.performance_tracker import PerformanceTracker
from modules.chart_generator import ChartGenerator


def load_config(config_file="config.json"):
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ Файл конфігурації не знайдено, використовую стандартні значення.")
        return {}


def process_request(params):
    print("🔍 process_request викликається")
    config = load_config()
    logger = Logger()
    tracker = PerformanceTracker(logger)
    collector = DataCollector(logger)
    processor = DataProcessor(logger)
    evaluator = PredictionEvaluator(logger)
    chart_gen = ChartGenerator(logger)

    # Параметри запиту
    stock = params.get("stock", [""]).strip()
    start_date = params.get("start_date", [""]).strip()
    end_date = params.get("end_date", [""]).strip()
    prediction = params.get("prediction", [""]).strip()

    logger.info(f"📊 Параметри запиту: stock={stock}, start_date={start_date}, end_date={end_date}, prediction={prediction}")
    if not (stock and start_date and end_date and prediction):
        return "<h2>⚠️ Усі поля форми повинні бути заповнені!</h2>"

    # Збір даних
    tracker.start("data_collection")
    data = collector.fetch_data(stock, start_date, end_date)
    tracker.stop("data_collection")

    if data.empty:
        return f"<h2>⚠️ Дані для акції {stock} за період {start_date} - {end_date} не знайдено або сталася помилка.</h2>"

    # Збереження csv
    os.makedirs("data", exist_ok=True)
    filename = f"data/{stock}_{start_date}_{end_date}.csv"
    data.to_csv(filename)
    logger.info(f"Дані збережено у файл {filename}")

    # Очищення і трансформація
    tracker.start("data_processing")
    cleaned_data = processor.clean_data(data)
    transformed_data = processor.transform_data(cleaned_data)
    tracker.stop("data_processing")

    # Оцінка прогнозу
    tracker.start("prediction_evaluation")
    error = evaluator.evaluate(filename, prediction)
    tracker.stop("prediction_evaluation")

    # Генерація графіку
    chart_path = chart_gen.generate_price_chart(filename, ticker=stock)
    chart_html = f'<p><img src="/{chart_path}" alt="Price Chart"></p>' if chart_path else ""

    # Звіт продуктивності
    report = tracker.generate_report()
    report_html = "<ul>" + "".join([f"<li>{line}</li>" for line in report]) + "</ul>"

    # Формування відповіді
    if error is not None:
        result_text = f"<p>Абсолютна помилка прогнозу: {error:.2f}</p>"
    else:
        result_text = "<p>Не вдалося оцінити прогноз.</p>"

    return f"""
    <h2>Результат для акції {stock} ({start_date} - {end_date}):</h2>
    <p>Дані збережено у файл: {filename}</p>
    {result_text}
    <h3>Графік динаміки цін:</h3>
    {chart_html}
    <h3>Звіт про продуктивність:</h3>
    {report_html}
    <p><a href="/">Повернутись до форми</a></p>
    """


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    import server  # Імпорт сервера, де є application

    with make_server("", 8000, server.application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
