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

    stock = params.get("stock", [""])[0].strip()
    start_date = params.get("start_date", [""])[0].strip()
    end_date = params.get("end_date", [""])[0].strip()
    prediction = params.get("prediction", [""])[0].strip()

    logger.info(f"📊 Параметри запиту: stock={stock}, start_date={start_date}, end_date={end_date}, prediction={prediction}")
    if not (stock and start_date and end_date and prediction):
        return "<h2>⚠️ Усі поля форми повинні бути заповнені!</h2>"

    tracker.start("data_collection")
    data = collector.fetch_data(stock, start_date, end_date)  # має повертати pd.DataFrame
    tracker.stop("data_collection")

    if all([df is None or df.empty for _, df in data]):
        return f"<h2>⚠️ Дані для акції {stock} за період {start_date} - {end_date} не знайдено або сталася помилка.</h2>"

    os.makedirs("data", exist_ok=True)
    files = []
    for site, df in data:
        filename = f"data/{site}_{stock}_{start_date}_{end_date}.csv"
        files.append(filename)
        df.to_csv(filename)
        logger.info(f"Дані збережено у файл {filename}")

    # tracker.start("data_processing")
    # cleaned_data = processor.clean_data(data)
    # transformed_data = processor.transform_data(cleaned_data)
    # tracker.stop("data_processing")

    tracker.start("prediction_evaluation")
    errors = evaluator.evaluate(data, prediction)
    tracker.stop("prediction_evaluation")

    chart_path = chart_gen.generate_price_chart(data, ticker=stock)
    chart_html = f'<p><img src="/{chart_path}" alt="Price Chart"></p>' if chart_path else ""

    report = tracker.generate_report()
    report_html = "<ul>" + "".join([f"<li>{line}</li>" for line in report]) + "</ul>"


    if errors:
        result_text = ""
        for site, error in errors:
            result_text += f"<p>Абсолютні помилка прогнозу ({site}): {error:.2f}</p>\n"
    if not errors:
        result_text = "<p>Не вдалося оцінити прогноз.</p>"


    return f"""
    <h2>Результат для акції {stock} ({start_date} - {end_date}):</h2>
    <p>Дані збережено у файли: <br>{'<br>'.join(files)}</p>
    <h3>Графік динаміки цін:</h3>
    {chart_html}
    <h3>Звіт про продуктивність:</h3>
    {report_html}
    <p><a href="/">Повернутись до форми</a></p>
    """


if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    import server

    try:
        with make_server("", 8000, server.application) as httpd:
            print("Serving on port 8000...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер зупинено користувачем (Ctrl+C).")

