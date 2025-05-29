import json

recipes = []

with open("recipes.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

current = {}
for line in lines:
    line = line.strip()
    if not line:
        continue
    if not line.startswith("INGREDIENTS:") and not line.startswith("DIRECTIONS:"):
        # Назва рецепта
        if current:
            recipes.append(current)
        current = {"TITLE": line}
    elif line.startswith("INGREDIENTS:"):
        ing_list = eval(line[len("INGREDIENTS:"):].strip())
        current["INGREDIENTS"] = ing_list
    elif line.startswith("DIRECTIONS:"):
        dir_list = eval(line[len("DIRECTIONS:"):].strip())
        current["DIRECTIONS"] = dir_list

# Додай останній рецепт
if current:
    recipes.append(current)

# Зберегти як JSON
with open("recipes.json", "w", encoding="utf-8") as out_f:
    json.dump(recipes, out_f, indent=2, ensure_ascii=False)

print(f"✅ Конвертовано {len(recipes)} рецептів у recipes.json")
