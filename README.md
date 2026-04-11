# Recipe Collection

An automated, web-based recipe management system. This repository hosts a collection of PDF recipes organized by category and served via a simple, responsive HTML interface.

## Project Structure

*   `index.html`: The main landing page that categorizes and links to all PDF recipes.
*   `pdfs/`: The storage directory for all recipe PDF files.
*   `styles.css`: Custom styling for the web interface.
*   `update_recipes.py`: The automation engine for the repository.
*   `logo.png`: Branding for the header.

## Automation Script (`update_recipes.py`)

The project includes a Python-based automation script that maintains the index and handles repository synchronization.

### What it does:
1.  **Normalization**: Automatically renames new PDF files to a web-friendly `snake_case` format (e.g., `Chicken_Fajitas.pdf` becomes `chicken_fajitas.pdf`).
2.  **Categorization**: Uses keyword analysis to automatically place new recipes into the correct HTML categories (Beef, Chicken, Pork, Breakfast, etc.).
3.  **Deduplication**: Ensures each recipe is only listed once in the main recipe list, while safely ignoring links in the "Weekly Menu" section.
4.  **Git Integration**: Automatically stages changes, commits them with an auto-generated message, and pushes them to the remote repository.

### How to use:
1.  Drop any new recipe PDF into the `pdfs/` folder.
2.  Run the update script:
    ```bash
    python update_recipes.py
    ```
3.  The script will handle the renaming, update `index.html`, and push the changes to GitHub.

## Requirements
*   Python 3.x
*   BeautifulSoup4 (`pip install beautifulsoup4`)
*   Git configured with saved credentials (for auto-push)

---
*Created and maintained by Justin Barnhill.*
