# Universal Website Scraper (MVP)

A full-stack application for scraping websites and viewing structured JSON output. Supports both static HTML and JavaScript-rendered content with interactive features like click flows, scrolling, and pagination.

## Features

- **Static Scraping**: Fast HTML parsing using httpx and selectolax
- **JS Rendering**: Fallback to Playwright for JavaScript-heavy sites
- **Interactive Scraping**: Click tabs, "Load more" buttons, and scroll/pagination
- **Section-Aware Parsing**: Intelligent section detection and grouping
- **Noise Filtering**: Removes cookie banners, popups, and overlays
- **JSON Viewer**: Beautiful React frontend to view and download results

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, httpx, selectolax, Playwright
- **Frontend**: React, Vite
- **Package Manager**: uv (Python), npm (Node.js)

## Setup & Installation

### Installation Steps

1. **Clone or navigate to the project directory**

2. **Make run.sh executable (Linux/Mac)**:
   ```bash
   chmod +x run.sh
   ```

3. **Run the setup script**:
   ```bash
   ./run.sh
   ```

   On Windows, simply run `run.bat`:
   ```cmd
   .\run.bat
   ```
   
   The script will automatically:
   - Install `uv` if it's not already installed
   - Create a virtual environment
   - Install all Python and frontend dependencies
   - Start the server

   Alternatively, you can use Git Bash/WSL with `run.sh`, or run the commands manually:
   ```powershell
   # Create virtual environment
   uv venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Install dependencies
   uv pip install -r requirements.txt
   
   # Install Playwright browsers
   python -m playwright install chromium
   
   # Install frontend dependencies
   cd frontend
   npm install
   npm run build
   cd ..
   
   # Start server
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

The server will start on `http://localhost:8000`

## Test URLs

Here are three primary URLs used for testing:

1. **https://en.wikipedia.org/wiki/Artificial_intelligence** - Scrapes the comprehensive article content about artificial intelligence, including sections on history, applications, and technical details.
2. **https://vercel.com/** - Scrapes the homepage content including product features, pricing information, and marketing copy from this modern JavaScript-rendered site.
3. **https://news.ycombinator.com/** - Scrapes the front page news articles, story titles, links, and discussion metadata from the Hacker News community platform.

## Project Structure

```
lyftr/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── routes/
│   │   ├── health.py        # Health check endpoint
│   │   └── scrape.py        # Scrape endpoint
│   └── scraper/
│       ├── static_scraper.py    # Static HTML scraper
│       ├── js_scraper.py        # Playwright JS scraper
│       ├── section_parser.py    # Section extraction
│       └── scraper_service.py   # Main orchestration
├── frontend/
│   ├── src/
│   │   ├── App.jsx          
│   │   └── App.css          
│   └── dist/                # Built frontend (generated)
├── run.sh                   # Setup and run script
├── requirements.txt         # Python dependencies
├── README.md               
├── design_notes.md         # Design decisions
└── capabilities.json       
```

## Limitations

1. **Single Domain**: The scraper focuses on the initial domain and doesn't follow cross-domain links
2. **Timeout Handling**: Some sites may block automation or take too long to load
3. **Rate Limiting**: No built-in rate limiting - be respectful when scraping
4. **Authentication**: Sites requiring login are not supported
5. **CAPTCHA**: Sites with CAPTCHA will fail gracefully with an error message
