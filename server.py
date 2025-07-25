from flask import Flask, request, send_from_directory, jsonify
import requests
import ollama
import json
import logging
from urllib.parse import urlparse
import os

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

from opentelemetry.instrumentation.flask import FlaskInstrumentor


app = Flask(__name__, static_url_path="")
client = ollama.Client(host=f"http://10.0.1.152:11434")

resource = Resource.create({"service.name": "com.thefossrant.portfolio-roast"})

# -- Tracing setup --

trace_provider = TracerProvider(resource=resource)
trace_exporter = OTLPSpanExporter(endpoint="http://10.0.1.152:4318/v1/traces")
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# -- Metrics setup --

metric_exporter = OTLPMetricExporter(endpoint="http://10.0.1.152:4318/v1/metrics")
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Create a histogram metric for response times (ms)
response_time_histogram = meter.create_histogram(
    name="http.server.response_time",
    unit="ms",
    description="Response time in milliseconds for HTTP requests"
)

# -- Logging setup --

logger_provider = LoggerProvider(resource=resource)
set_logger_provider(logger_provider)
log_exporter = OTLPLogExporter(endpoint="http://10.0.1.152:4318/v1/logs")
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
logging.getLogger().addHandler(handler)
logger = logging.getLogger(__name__)

# Instrument Flask
FlaskInstrumentor().instrument_app(app)



def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@app.route("/<path:path>")
def serve_static(path):
    meter.create_counter(
        name="http.server.static_requests",
        unit="requests",
        description="Static web requests"
    ).add(1)
    return send_from_directory("static", path)


@app.route("/")
def serve_index():
    meter.create_counter(
        name="http.server.static_requests",
        unit="requests",
        description="Static web requests"
    ).add(1)
    return send_from_directory("static", "index.html")

ollama_error_counter = meter.create_counter(
    name="ollama.errors",
    unit="errors",
    description="Number of Ollama API errors"
)

@app.route("/api", methods=["POST"])
def api_endpoint():
    meter.create_counter(
        name="http.server.api_calls",
        unit="requests",
        description="API Calls"
    ).add(1)
    data = request.json
    html = ""
    if not is_valid_url(data["url"]):
        return
    res = requests.get(data["url"])
    if res.status_code == 200:
        html = res.text
    else:
        return "your portfolio so bad that i dont even know how to roast it"
    try:
        jsonres = client.chat(
            model="gemma:2b",
            messages=[
                {
                    "role": "user",
                    "content": f"I will provide the raw HTML of a developer portfolio site. Please roast the content of the website (dont comment about the actual code) and make your response super funny. Don't criticize it or suggest improvements, roast it, like put it on a grill until it is charred. Don't list the specific issues with the site, just slam the entire webpage in general. Also please make the point-of-view as if you are the one actually viewing the webpage and roasting it: f{html}",
                }
            ],
        )
        return jsonres["message"]["content"]
    except Exception as e:
        ollama_error_counter.add(1)
        logger.error(e, exc_info=True)
        return jsonify({"error": "Ollama failed to roast your portfolio."}), 500


if __name__ == "__main__":
    app.run(debug=True)
