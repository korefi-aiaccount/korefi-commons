# KoreFi Commons

Common utilities for KoreFi projects.

.
├── analytics_models
│   └── django
│       ├── ap.py
│       └── ar.py
├── filepath_generator.py
├── s3.py
└── s3uri_generator.py

## Installation

```bash
pip install git+https://bitbucket.org/korefi/korefi-commons.git
```

## Usage

```python
from korefi_commons.s3 import S3Service
```

## Development

1. Clone the repository
2. Create virtual environment: `python -m venv .venv`
3. Activate: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run tests: `pytest` 