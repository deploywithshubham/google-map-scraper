# Google Maps Scraper

This is a Python-based Google Maps Scraper that lets you extract business details like name, address, phone number, website, category, coordinates, and reviews directly from Google Maps. The project supports:

- CLI-based scraping

## Features

- Deduplication logic to prevent duplicate entries
- Saves to keyword-specific CSV and master CSV
- Supports multiple keywords via input.txt
- Extracts: name, phone, website, address, category, reviews, and GPS coordinates

## Requirements

- Install dependencies with:
- ``` pip install -r requirements.txt ```

### Required packages

- playwright
- pandas
- openpyxl
- requests
- beautifulsoup4
- lxml
- python-dotenv

## One-Time Setup

 ``` playwright install ```

## How to Use
