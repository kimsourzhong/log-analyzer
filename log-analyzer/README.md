# Log Analyzer

A lightweight web app that parses application log files, groups errors by
recurring pattern, and highlights the most frequent issues — a simplified
version of the kind of log monitoring and known-issue tracking a support
engineer does in production.

## Why I built this

Application support roles involve monitoring logs, spotting recurring
problems, and turning them into known-issue documentation. This project is
a small, self-contained way to demonstrate that workflow: upload a log file,
and the tool automatically surfaces error rates, which regions/components
are affected, and which specific problems keep recurring.

## Features

- Parses structured log lines (timestamp, level, component, region, message)
- Groups similar error messages together (e.g. treats "Timeout after 30s"
  and "Timeout after 45s" as the same underlying issue)
- Shows error/warning counts, error rate, and breakdowns by region and level
- Exports parsed results as CSV
- Comes with a bundled sample log so it works out of the box

## Tech stack

- Python
- Streamlit (UI + hosting)
- Pandas (data processing)
- Regex-based log parsing

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Deploy it for free (Streamlit Community Cloud)

1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click "New app", select your repo, and set the main file to `app.py`.
4. Click Deploy — you'll get a live shareable URL in about a minute.

## Possible extensions

- Support additional log formats via configurable parsing rules
- Add a "mark as known issue" button that saves patterns to a small database
- Add alerting (e.g. flag when error rate crosses a threshold)
- Add time-series charts to show error trends over time, not just totals
