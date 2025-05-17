import os
from datetime import datetime


class ReportGenerator:
    def __init__(self, logger, report_dir="reports"):
        self.logger = logger
        os.makedirs(report_dir, exist_ok=True)
        self.report_file = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y-%m-%d')}.txt")

    def generate_report(self, summary):
        self.logger.log("Generating final report...")
        with open(self.report_file, "w") as f:
            f.write("💼 Stock Analyzer Report\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🕒 Total Execution Time: {summary['execution_time']:.2f} seconds\n\n")

            f.write("📊 Data Collection Summary\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Sources: {summary['total_sources']}\n")
            f.write(f"Successfully Processed: {summary['successful_sources']}\n")
            f.write(f"Failed: {summary['failed_sources']}\n")
            f.write(f"Total Rows Collected: {summary['total_rows']}\n")
            f.write(f"Total Columns Collected: {summary['total_columns']}\n\n")

            f.write("❗️ Error Report\n")
            f.write("-" * 30 + "\n")
            for url, error in summary['failed_details']:
                f.write(f"- {url} ({error})\n")

            f.write("\n📝 Data Stats\n")
            f.write("-" * 30 + "\n")
            for url, rows, columns in summary['data_stats']:
                f.write(f"- {url}: {rows} rows, {columns} columns\n")

            self.logger.log(f"Report saved to {self.report_file}")
