# Adaptive Intelligent Data Compression Engine

An end-to-end data pipeline system that dynamically profiles incoming data streams, evaluates entropy and repetition, and autonomously selects the most optimal compression technique based on characteristics and size.

## Features

- **Data Profiling**: Scans data to determine Entropy (Shannon), repetition ratio, and file size.
- **Intelligent Decision Engine**: A rule-based architecture that dynamically selects the best compression strategy (`gzip`, `lz4`, `zstd`, `none`).
- **Performance Execution & Monitoring**: Built-in wrappers around `psutil` track specific CPU overhead, elapsed execution time, and storage savings.
- **Historical Learning/Feedback Map**: A SQLite memory map (`storage.db`) inherently stores logs for retrospective dashboard review.
- **Interactive UI**: Complete pipeline built dynamically out of Streamlit with dataset selections and chart visualization.

## Modules

```text
working model/
├── data/                         # Samples & Compressed Outputs
├── core/                         
│   ├── profiler.py               # Entropy generation and byte processing
│   ├── compression.py            # The actual algorithms
│   ├── decision_engine.py        # Logic mapping
│   └── monitoring.py             # Performance measurement
├── storage/                      
│   └── feedback_db.py            # SQLite data tracking
├── tools/
│   └── generate_datasets.py      # Synthesize test data
└── app.py                        # Streamlit web-app wrapper
```

## Running the Application

Ensure you have all standard requirements installed via:
```sh
pip install -r requirements.txt
```

Run the application:
```sh
streamlit run app.py
```
