# Google Maps Scraper

This is a Python-based Google Maps Scraper that lets you extract business details like name, address, phone number, website, category, coordinates, and reviews directly from Google Maps. The project supports:

- CLI-based scraping

## Features

- Deduplication logic to prevent duplicate entries
- Saves to keyword-specific CSV and master CSV
- Supports multiple keywords via input.txt
- Extracts: name, phone, website, address, category, reviews, and GPS coordinates

## Download Python if not installed

```markdown
https://www.python.org/downloads/
```

### Install pip (Python’s package manager)

- Open Command Prompt and run:

```markdown
python -m ensurepip --upgrade
```

- Or download and run the official get-pip.py:

```markdown
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
```

```markdown
python get-pip.py
```

## Download Repository

- via HTTPS

```markdown
git clone https://github.com/deploywithshubham/google-map-scraper.git
```

## Requirements

- Install dependencies with:

```markdown
pip install -r requirements.txt
```

### Required packages

- playwright
- pandas
- openpyxl
- requests
- beautifulsoup4
- lxml
- python-dotenv

### One-Time Setup

 ```markdown
 playwright install 
 ```

## How to Use

```markdown
python main.py -s "hotels in london" -t 10
```

- s: Search keyword
- t: Number of new unique results

## Output

Scraped data will be saved in:

- GMaps Data → all_scraped_master.csv → YYYY-MM-DD → hotels in london.csv

## Notes

- Only new businesses (not previously scraped) will be saved.
- Make sure your internet is stable while scraping Google Maps.
- Headless mode is disabled for debugging and visibility.

## License

This project is licensed for personal or educational use. Use responsibly and avoid violating Google Maps terms of service.
