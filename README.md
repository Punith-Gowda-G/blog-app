# Inkwell Blog 📝

A clean, editorial-style blog built with Flask + SQLite.

## Features
- 🏠 Home page with post grid
- 📖 Full blog post detail view
- ✍️  Create new posts
- ✏️  Edit existing posts
- 🗑️  Delete posts (with confirmation)
- 🔍 Search by keyword
- 🏷️  Filter by category

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py
```

Then open **http://127.0.0.1:5000** in your browser.

## Project Structure
```
blog/
├── app.py               ← Flask routes + DB logic
├── blog.db              ← SQLite database (auto-created)
├── requirements.txt
├── templates/
│   ├── base.html        ← Shared layout & header
│   ├── index.html       ← Home page
│   ├── post_detail.html ← Single post view
│   └── post_form.html   ← Create / Edit form
└── static/
    ├── style.css        ← All styles
    └── main.js          ← Search, word count, confirmations
```

## Tech Stack
- **Backend**: Python / Flask
- **Database**: SQLite (via Python's built-in `sqlite3`)
- **Frontend**: HTML + CSS + Vanilla JS
- **Fonts**: Playfair Display + DM Sans (Google Fonts)
