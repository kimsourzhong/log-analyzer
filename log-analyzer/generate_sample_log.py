"""
Generates a realistic-looking sample application log file (sample_log.txt)
so the Log Analyzer app has something to demo with immediately.
Run: python generate_sample_log.py
"""
import random
from datetime import datetime, timedelta

LEVELS = ["INFO", "WARNING", "ERROR", "CRITICAL"]

MESSAGES = [
    ("INFO", "Request completed successfully", "api"),
    ("INFO", "User authenticated", "auth"),
    ("INFO", "Health check passed", "healthcheck"),
    ("WARNING", "Database connection pool nearing capacity", "database"),
    ("WARNING", "Retrying request after timeout", "api"),
    ("WARNING", "Deprecated endpoint called", "api"),
    ("ERROR", "Database connection timeout", "database"),
    ("ERROR", "Failed to parse OCR image: unsupported format", "ocr"),
    ("ERROR", "NullReferenceException in report generation", "reporting"),
    ("ERROR", "Kubernetes pod restarted unexpectedly", "infra"),
    ("ERROR", "Authentication token expired mid-session", "auth"),
    ("CRITICAL", "Service unavailable: 502 from upstream", "infra"),
    ("CRITICAL", "Out of memory error in worker process", "infra"),
]

REGIONS = ["AU-East", "ZA-South", "ID-Central", "QLD-Central"]

def generate(num_lines=400, out_path="sample_log.txt"):
    start = datetime.now() - timedelta(hours=6)
    lines = []
    for i in range(num_lines):
        ts = start + timedelta(seconds=i * random.randint(3, 20))
        level, msg, component = random.choice(MESSAGES)
        # Weight towards INFO/WARNING so ERROR/CRITICAL are the "interesting" minority
        if random.random() < 0.55:
            level, msg, component = random.choice(
                [m for m in MESSAGES if m[0] == "INFO"]
            )
        region = random.choice(REGIONS)
        lines.append(
            f"{ts.strftime('%Y-%m-%d %H:%M:%S')} [{level}] ({component}) region={region} - {msg}"
        )
    with open(out_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {num_lines} lines to {out_path}")

if __name__ == "__main__":
    generate()
