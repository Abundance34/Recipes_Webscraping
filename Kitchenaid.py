import requests
from bs4 import BeautifulSoup
import json

# List of KitchenAid recipe URLs
urls = [
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-butter.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/cinnamon-roll-bread.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-butter-biscuit-dough.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-a-cake-with-a-stand-mixer.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-banana-bread.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-baobing.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-bingsu.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-buttercream-frosting.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-chocolate-chip-cookies.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-chocolate-ice-cream.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-cream-cheese-frosting.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-fettuccine-noodles.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-frozen-yogurt.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-hawaiian-shave-ice.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-homemade-pasta.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-homemade-pie-crust.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-ice-cream-cake.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-italian-ice.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-kakigori.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-mashed-potatoes.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-piraguas.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-pizza-dough.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-quiche.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-raspados.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-ravioli.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-rye-bread.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-sandwich-bread.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-swedish-meatballs.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-vanilla-ice-cream.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-veggie-noodles.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-make-whipped-cream.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-shred-chicken.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/how-to-stuff-sausage.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/stand-mixer-cookie-recipes.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/stand-mixer-recipes.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/tips-for-making-bread-with-stand-mixer.html",
    "https://www.kitchenaid.com/pinch-of-help/stand-mixers/vegetable-sheet-cutter-recipes-and-uses.html",
]

# Set headers to mimic a real browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Store all recipes
all_recipes = []

# Scrape each URL
for url in urls:
    recipe_data = {"source": url}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract JSON-LD if present
            script_tag = soup.find("script", type="application/ld+json")
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    if isinstance(json_data, list):
                        json_data = json_data[0]
                    recipe_data.update(json_data)
                except Exception as e:
                    print(f"Error parsing JSON-LD from {url}: {e}")

            # Manual fallback extraction
            if "name" not in recipe_data:
                title = soup.find("h1")
                recipe_data["title"] = title.get_text(strip=True) if title else "No title found"

            # Extract ingredients
            ingredients = []
            ingredients_heading = soup.find(lambda tag: tag.name == "h2" and "ingredients" in tag.get_text(strip=True).lower())
            if ingredients_heading:
                ingredients_list = ingredients_heading.find_next_sibling()
                if ingredients_list and ingredients_list.name in ["ul", "ol"]:
                    ingredients = [li.get_text(strip=True) for li in ingredients_list.find_all("li")]
            recipe_data["ingredients"] = ingredients if ingredients else "No ingredients found"

            # Extract preparation steps
            steps = []
            step_headings = soup.find_all(lambda tag: tag.name == "h3" and "step" in tag.get_text(strip=True).lower())
            for heading in step_headings:
                step_text = heading.get_text(strip=True)
                next_paragraph = heading.find_next_sibling()
                if next_paragraph and next_paragraph.name == "p":
                    step_text += " " + next_paragraph.get_text(strip=True)
                steps.append(step_text)
            recipe_data["steps"] = steps if steps else "No preparation steps found"

            all_recipes.append(recipe_data)
        else:
            print(f"Failed to fetch {url} - Status code: {response.status_code}")
    except Exception as ex:
        print(f"Error processing {url}: {ex}")

# Save all recipe data to a JSON file
with open("kitchenaid_recipes.json", "w", encoding="utf-8") as f:
    json.dump(all_recipes, f, ensure_ascii=False, indent=4)

print("All recipe data saved to 'kitchenaid_recipes.json'")
