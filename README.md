# PurchaseTracker

A comprehensive purchase tracking application designed to help users monitor, categorize, and analyze their spending habits.

## Features

- **Purchase Tracking**: Record and manage your purchases with detailed information
- **Categorization**: Organize purchases with a customizable category system
- **Analytics**: Gain insights through spending trends, category breakdowns, and visual reports
- **Data Import/Export**: Import purchases from CSV/bank statements and export data for external use

## Tech Stack

- **Backend**: Python with FastAPI
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **ORM**: SQLModel (combines SQLAlchemy and Pydantic)
- **Analytics**: Pandas, Plotly
- **Testing**: Pytest

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/purchase-tracker.git
cd purchase-tracker
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development

```bash
uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000, and the interactive API documentation at http://localhost:8000/docs.

### Production

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
purchase-tracker/
├── data/               # Data storage
├── src/                # Application source code
│   ├── modeling/       # ML models for categorization
│   └── services/       # Application services
├── tests/              # Unit and integration tests
├── PLANNING.md         # Project planning documentation
└── README.md           # Project documentation
```

## Development

### Testing

Run the test suite:

```bash
pytest
```

### Code Quality

Format the code using Black:

```bash
black src tests
```

## License

MIT

## Web Frontend

A simple web frontend is now available in `src/web/`.

### Features
- Login/logout with FastAPI backend
- Add new purchases (amount, description, date, category)
- View list of purchases in a table
- Responsive, modern UI (HTML/CSS/JS)

### Usage
1. Start the FastAPI backend (see above).
2. Serve the frontend files in `src/web/` using any static file server, or configure FastAPI to serve them.
3. Open `index.html` in your browser.

### Dependencies
- No build step required; pure HTML/CSS/JS.

### Setup Example (with FastAPI static files):
Add the following to your FastAPI app:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="src/web"), name="static")
```

Then access the frontend at `http://localhost:8000/static/index.html`.

---
