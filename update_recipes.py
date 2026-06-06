import os
import re
import subprocess
from bs4 import BeautifulSoup

# Configuration
PDF_DIR = 'pdfs'
INDEX_FILE = 'index.html'

CATEGORIES = {
    "Breakfast": ["bfast", "breakfast", "pancake", "mcgriddle", "oatmeal", "french_toast", "egg"],
    "Chicken / Turkey": ["chicken", "turkey", "buffalo", "wing", "cordonbleu", "bryan", "firecracker"],
    "Seafood": ["shrimp", "fish", "salmon", "scampi", "seafood"],
    "Pork": ["pork", "ribs", "sausage", "ham", "bacon"],
    "Beef": ["beef", "burger", "steak", "meatloaf", "taco", "sloppy_joe", "meatball", "barbacoa", "fajita", "chimichanga", "crunchwrap", "enchilada"],
    "Dessert / Baking": ["cake", "cookie", "bread", "icing", "dessert", "pie", "cheesecake", "sugar", "mounds", "luna"],
    "Sauces / Misc": ["sauce", "oil", "margarita", "cilantro", "alfredo", "dressing"],
    "Misc / Pasta / Sides": [] # Fallback
}

def normalize_name(filename):
    name, ext = os.path.splitext(filename)
    name = name.lower()
    name = re.sub(r'[\s\-_]+', '_', name)
    name = re.sub(r'[^\w]', '', name)
    return name + ext

def get_category(filename):
    name = filename.lower()
    if "shepherds_pie" in name:
        return "Misc / Pasta / Sides"
    if "chicken" in name or "turkey" in name:
        return "Chicken / Turkey"
    if "shrimp" in name or "scampi" in name or "fish" in name:
        return "Seafood"
    for category, keywords in CATEGORIES.items():
        if category == "Misc / Pasta / Sides":
            continue
        for kw in keywords:
            if kw in name:
                return category
    return "Misc / Pasta / Sides"

def format_title(filename):
    name, _ = os.path.splitext(filename)
    return name.replace('_', ' ').title()

def sync_to_git():
    """Stages, commits, and pushes changes to git."""
    try:
        # Check for changes
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout.strip()
        if not status:
            print("No changes detected. Skipping git sync.")
            return

        print("\nChanges detected. Syncing to git...")
        
        # Stage all changes (including renames and index.html)
        subprocess.run(['git', 'add', '-A'], check=True)
        
        # Commit with a descriptive message
        commit_msg = "Auto-update: Renamed recipes and updated index.html"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # Push to remote
        print("Pushing to remote repository...")
        subprocess.run(['git', 'push'], check=True)
        
        print("Git sync complete.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git sync: {e}")
    except FileNotFoundError:
        print("Error: 'git' command not found. Please ensure git is installed and in your PATH.")

def main():
    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Rename files on disk
    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith('.pdf') or filename in ['.DS_Store', 'Thumbs.db']:
            continue
        
        normalized = normalize_name(filename)
        if filename != normalized:
            old_path = os.path.join(PDF_DIR, filename)
            new_path = os.path.join(PDF_DIR, normalized)
            
            if os.path.exists(new_path) and filename.lower() != normalized.lower():
                print(f"Warning: {new_path} already exists. Skipping rename for {filename}.")
            else:
                print(f"Renaming: {filename} -> {normalized}")
                if filename.lower() == normalized.lower():
                    temp_path = os.path.join(PDF_DIR, normalized + ".tmp")
                    os.rename(old_path, temp_path)
                    os.rename(temp_path, new_path)
                else:
                    os.rename(old_path, new_path)

    # 2. Normalize all links in the document
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('pdfs/'):
            filename = os.path.basename(href)
            normalized = normalize_name(filename)
            a['href'] = f"pdfs/{normalized}"

    # 3. Deduplicate links ONLY within the 'recipes' div
    recipes_div = soup.find('div', class_='recipes')
    if recipes_div:
        seen_links = set()
        to_remove = []
        for a in recipes_div.find_all('a', href=True):
            href = a['href']
            if href.startswith('pdfs/'):
                if href in seen_links:
                    li = a.find_parent('li')
                    if li:
                        to_remove.append(li)
                else:
                    seen_links.add(href)
        
        for li in to_remove:
            li.decompose()

    # 4. Add missing links to 'recipes' div
    linked_in_recipes = set()
    if recipes_div:
        for a in recipes_div.find_all('a', href=True):
            href = a['href']
            if href.startswith('pdfs/'):
                linked_in_recipes.add(os.path.basename(href))

    new_files_added = 0
    for filename in os.listdir(PDF_DIR):
        if not filename.lower().endswith('.pdf') or filename in ['.DS_Store', 'Thumbs.db']:
            continue
        
        if filename not in linked_in_recipes:
            category = get_category(filename)
            title = format_title(filename)
            print(f"Adding missing/new recipe: {title} to category {category}")

            h1 = soup.find('h1', string=re.compile(re.escape(category), re.IGNORECASE))
            if not h1:
                h1 = soup.find('h1', string=re.compile("Misc / Pasta / Sides", re.IGNORECASE))
            
            if h1:
                ul = h1.find_next_sibling('ul')
                if ul:
                    new_li = soup.new_tag('li')
                    new_a = soup.new_tag('a', href=f'pdfs/{filename}')
                    new_a.string = title
                    new_li.append(new_a)
                    ul.append(new_li)
                    new_files_added += 1
                    linked_in_recipes.add(filename)

    # 5. Alphabetize all lists in the recipes div
    if recipes_div:
        for ul in recipes_div.find_all('ul'):
            # Get all li items
            items = ul.find_all('li')
            # Sort items by the text content (case-insensitive)
            items.sort(key=lambda li: li.get_text(strip=True).lower())
            # Clear the current ul
            ul.clear()
            # Re-append sorted items
            for li in items:
                ul.append(li)

    # Save changes
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print(f"Local updates finished. Total recipes added: {new_files_added}")
    
    # Final Step: Git Sync
    sync_to_git()

if __name__ == "__main__":
    main()
