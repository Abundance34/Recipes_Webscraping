import requests
from bs4 import BeautifulSoup
import json
import time
import os  # Added missing import

# Set up output path
OUTPUT_FILE = os.path.join(os.path.expanduser('~'), 'Documents', 'cookpad_recipes.jsonl')

def scrape_cookpad_recipe(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data
        title = soup.find('h1').text.strip() if soup.find('h1') else "No title"

        ingredients = []
        for ing in soup.select('[class*=ingredient]'):
            text = ing.get_text(strip=True)
            if text and text not in ingredients:
                ingredients.append(text)

        steps = []
        step_elements = soup.find_all('div', class_='step__text') or soup.find_all('li', class_='step')
        for idx, step in enumerate(step_elements, 1):
            steps.append(f"Step {idx}: {step.get_text(strip=True)}")

        return {
            "title": title,
            "url": url,
            "ingredients": ingredients,
            "steps": steps
        }

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

# Properly formatted URL list
urls = [
    "https://cookpad.com/ng/recipes/24515127-carrot-smoothie",
    "https://cookpad.com/ng/recipes/24619510-chicken-and-potatoes-samosa-and-a-simple-shawarma",
    "https://cookpad.com/ng/recipes/24429283-best-shawarma-recipe",
    "https://cookpad.com/ng/recipes/24704703-cherry-polenta-cake-regular-or-dairy-free",
    "https://cookpad.com/ng/recipes/24379286-dairy-free-double-chocolate-cake-with-dairy-free-peanut-butter-icing",
    "https://cookpad.com/ng/recipes/17036773-dairy-free-tangerine-dessert",
    "https://cookpad.com/ng/recipes/24109920-dairy-free-carrot-cake",
    "https://cookpad.com/ng/recipes/23860029-creamy-dairy-free-pumpkin-vodka-pasta",
    "https://cookpad.com/ng/recipes/23845289-mild-dairy-free-kashmiri-chicken-curry",
    "https://cookpad.com/ng/recipes/22659338-dairy-egg-free-pancake",
    "https://cookpad.com/ng/recipes/22588009-muskmelon-carrot-smoothie-dairy-free",
    "https://cookpad.com/ng/recipes/22547911-mango-papaya-smoothie-dairy-free",
    "https://cookpad.com/ng/recipes/22543533-sugar-free-dairy-free-makhana-custard-vegan",
    "https://cookpad.com/ng/recipes/24368528-california-farm-saffron-vegan-and-dairy-butter",
    "https://cookpad.com/ng/recipes/17312985-mussels-and-mushroom-risotto-dairy-free",
    "https://cookpad.com/ng/recipes/17298716-dairy-free-lemon-mousse",
    "https://cookpad.com/ng/recipes/17215519-dairy-free-crustless-quiche",
    "https://cookpad.com/ng/recipes/17280936-mixed-fruit-smoothie-dairy-free",
    "https://cookpad.com/ng/recipes/17187826-dairy-free-canned-apple-cake",
    "https://cookpad.com/ng/recipes/17116981-dairy-free-mango-avocado-smoothie",
    "https://cookpad.com/ng/recipes/17064546-creamy-dairy-free-potato-soup",
    "https://cookpad.com/ng/recipes/16967457-dairy-free-pastry-cream",
    "https://cookpad.com/ng/recipes/16929255-dairy-free-melkkos",
    "https://cookpad.com/ng/recipes/16925260-dairy-free-milktart",
    "https://cookpad.com/ng/recipes/16906337-silken-tofu-cocoa-muffins-dairy-free",
    "https://cookpad.com/ng/recipes/16736171-prawn-and-gnocchi-with-dairy-free-creamy-garlic-cheese-sauce",
    "https://cookpad.com/ng/recipes/16681600-dairy-free-creamy-garlic-pork",
    "https://cookpad.com/ng/recipes/16629854-moist-dairy-free-eggless-chocolate-chip-cupcakes",
    "https://cookpad.com/ng/recipes/16577406-dairy-free-pancakes",
    "https://cookpad.com/ng/recipes/16421636-dairy-free-creamy-tuscan-chicken",
    "https://cookpad.com/ng/recipes/16313102-amazing-dairy-free-potato-bake",
    "https://cookpad.com/ng/recipes/16199928-dairy-free-tzatziki",
    "https://cookpad.com/ng/recipes/16173382-dairy-free-tropical-oats-cookies",
    "https://cookpad.com/ng/recipes/17302094-datecarrot-and-walnut-cake",
    "https://cookpad.com/ng/recipes/15443150-crumb-cake-dairy-free",
    "https://cookpad.com/ng/recipes/15171118-dairy-free-banana-cake",
    "https://cookpad.com/ng/recipes/15074246-stove-top-cake-with-tofu-cream-gluten-and-dairy-free",
    "https://cookpad.com/ng/recipes/14814618-brooklyn-butternut-blackout-cake-wheat-free",
    "https://cookpad.com/ng/recipes/13650882-apple-cardamom-pound-cake-low-histamine-gluten-free-dairy-free-vegan-corn-free",
    "https://cookpad.com/ng/recipes/13564672-ollies-handy-maple-cakes-low-histamine-gluten-free-dairy-free-vegan-corn-free",
    "https://cookpad.com/ng/recipes/13361515-dairy-free-spiced-clementine-cake",
    "https://cookpad.com/ng/recipes/14360560-gluten-free-fairy-cakes",
    "https://cookpad.com/ng/recipes/14049102-gulab-tres-leches-cake-gluten-free",
    "https://cookpad.com/ng/recipes/14168641-free-from-pineapple-upside-down-cakes-baking",
    "https://cookpad.com/ng/recipes/13027076-double-chocolate-celebration-cake-eggless-vegan-easy-dairy-free",
    "https://cookpad.com/ng/recipes/13955057-oats-cake-gluten-free-and-sugar-free",
    "https://cookpad.com/ng/recipes/15245019-ragi-chocolate-mug-cake",
    "https://cookpad.com/ng/recipes/14978025-vegan-welsh-cakes",
    "https://cookpad.com/ng/recipes/14445547-easy-vegan-carrot-cake",
    "https://cookpad.com/ng/recipes/10938841-vegan-banana-bread-cake-egglesssugar-free-and-dairy-free",
    "https://cookpad.com/ng/recipes/10747174-cranberry-cake-with-hot-butter-cream-sauce-glutendairy-free",
    "https://cookpad.com/ng/recipes/13995645-chocolate-peanut-butter-mug-cake",
    "https://cookpad.com/ng/recipes/13932110-flourless-chocolate-cake",
    "https://cookpad.com/ng/recipes/13907184-beetroot-chocolate-cake-with-avocado-frosting",
    "https://cookpad.com/ng/recipes/12868528-carrot-cake",
    "https://cookpad.com/ng/recipes/12868480-caramel-banana-cake",
    "https://cookpad.com/ng/recipes/12868442-mini-double-chocolate-berry-cakes",
    "https://cookpad.com/ng/recipes/12747406-carrot-cake-pancakes",
    "https://cookpad.com/ng/recipes/12696542-spiced-apple-cake",
    "https://cookpad.com/ng/search_filters/dairy%20free%20cookies",
    "https://cookpad.com/ng/recipes/24049172-chocolate-chip-cookies",
    "https://cookpad.com/ng/recipes/15516203-dairy-free-snow-cookies",
    "https://cookpad.com/ng/recipes/15223742-dairy-free-vegan-chocolate-chip-cookies",
    "https://cookpad.com/ng/recipes/13963390-pecan-maple-chocolate-chip-cookies-low-sugar-grain-dairy-free",
    "https://cookpad.com/ng/recipes/13367908-alis-gluten-free-dairy-free-chocolate-chip-coconut-rum-cookies",
    "https://cookpad.com/ng/recipes/12191099-traditional-walnut-horseshoe-cookies-orasnice-gluten-free-flourless-dairy-free-vegetarian",
    "https://cookpad.com/ng/recipes/14320293-chocl-oaty-white-cranberry-cookies",
    "https://cookpad.com/ng/recipes/14177549-candy-cane-chocolate-cookies",
    "https://cookpad.com/ng/recipes/13757483-peanut-butter-oatmeal-chocolate-chip-cookies",
    "https://cookpad.com/ng/recipes/12777059-stem-ginger-cookies",
    "https://cookpad.com/ng/recipes/12696588-peanut-butter-choc-chip-cookies",
    "https://cookpad.com/ng/recipes/12670544-chocolate-pb-sandwich-cookies",
    "https://cookpad.com/ng/recipes/6787683-chocolate-cookies-gluten-dairy-free",
    "https://cookpad.com/ng/recipes/11163151-vegan-chocolate-chip-cookies",
    "https://cookpad.com/ng/recipes/1668089-cutout-cookies-egg-soy-dairy-gluten-free-corn-lite",
    "https://cookpad.com/ng/recipes/3250974-vegan-chocolate-chip-cookie-skillet",
    "https://cookpad.com/ng/recipes/738565-dairy-and-gluten-free-peanut-butter-cookies",
    "https://cookpad.com/ng/recipes/349259-gluten-and-dairy-free-banana-chocolate-chip-cookies",
    "https://cookpad.com/ng/recipes/313651-ragi-bajra-and-wholewheat-shortbread-cookies-with-pumpkin-pie-spice",
    "https://cookpad.com/ng/recipes/343231-vickys-remembrance-day-lemon-poppy-seed-cookies-gf-df-ef-sf-nf",
    "https://cookpad.com/ng/recipes/349554-peanut-mm-cookies",
    "https://cookpad.com/ng/recipes/355462-vickys-apple-cookies-gluten-dairy-egg-soy-free",
    "https://cookpad.com/ng/recipes/152810-dairy-free-strawberry-cookies",
    "https://cookpad.com/ng/recipes/144084-egg-and-dairy-free-crispy-cookies",
    "https://cookpad.com/ng/recipes/149155-egg-and-dairy-free-raisin-cookies",
    "https://cookpad.com/ng/recipes/151066-food-allergy-friendly-dairy-egg-free-cookies",
    "https://cookpad.com/ng/recipes/145301-egg-and-dairy-free-whole-wheat-flour-and-honey-cookies",
    "https://cookpad.com/ng/recipes/146962-easy-crispy-dairy-free-cookies-made-with-pancake-mix",
    "https://cookpad.com/ng/recipes/352736-vegan-chocolate-peanut-butter-cookies",

]

# Scrape all recipes with delay
all_recipes = []
for url in urls:
    print(f"Scraping: {url}")
    recipe = scrape_cookpad_recipe(url)
    if recipe:
        all_recipes.append(recipe)
    time.sleep(2)

print(f"📁 Will save recipes to: {os.path.abspath(OUTPUT_FILE)}")

# Save to JSONL (one JSON object per line)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    for recipe in all_recipes:
        json_line = json.dumps(recipe, ensure_ascii=False)
        f.write(json_line + '\n')

print(f"✅ Saved {len(all_recipes)} recipes to {OUTPUT_FILE}")