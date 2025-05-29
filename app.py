import os
import glob
import shutil
import time
import streamlit as st
from ultralytics import YOLO
from googletrans import Translator

# Перекладач
translator = Translator()

def translate_text(text, dest_lang="uk"):
    try:
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        return f"[Помилка перекладу: {e}]"

# модель
@st.cache_resource
def load_model():
    return YOLO("best.pt")

model = load_model()

st.title("🥦 Метод штучного інтелекту для автоматичної побудови можливих рецептів страв за зображеннями продуктів")

uploaded_file = st.file_uploader("Завантаж зображення", type=["jpg", "jpeg", "png"])

if uploaded_file:
    timestamp = str(int(time.time()))
    image_path = f"temp_image_{timestamp}.jpg"

    with open(image_path, "wb") as f:
        f.write(uploaded_file.read())

    # Очистка попередніх результатів
    temp_dir = os.path.join("runs", "detect", "predict")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    # Розпізнавання
    results = model.predict(
        source=image_path,
        save=True,
        save_dir=temp_dir,
        show=False
    )

    # Збереження зображень (оригіналу та обробленого)
    os.makedirs("saved_images/original", exist_ok=True)
    os.makedirs("saved_images/processed", exist_ok=True)
    shutil.copy(image_path, os.path.join("saved_images/original", f"{timestamp}.jpg"))

    # дозволенні обʼєкти
    names = model.names
    allowed_objects = {'Akabare Khursani', 'Apple', 'Artichoke', 'Ash Gourd -Kubhindo-', 'Asparagus -Kurilo-', 'Avocado', 
                       'Bacon', 'Bamboo Shoots -Tama-', 'Banana', 'Beans', 'Beaten Rice -Chiura-', 'Beef', 'Beetroot', 
                       'Bethu ko Saag', 'Bitter Gourd', 'Black Lentils', 'Black beans', 'Bottle Gourd -Lauka-', 'Bread', 
                       'Brinjal', 'Broad Beans -Bakullo-', 'Broccoli', 'Buff Meat', 'Butter', 'Cabbage', 'Capsicum', 'Carrot', 
                       'Cassava -Ghar Tarul-', 'Cauliflower', 'Chayote-iskus-', 'Cheese', 'Chicken', 'Chicken Gizzards', 
                       'Chickpeas', 'Chili Pepper -Khursani-', 'Chili Powder', 'Chowmein Noodles', 'Cinnamon', 
                       'Coriander -Dhaniya-', 'Corn', 'Cornflakec', 'Crab Meat', 'Cucumber', 'Egg', 'Farsi ko Munta', 
                       'Fiddlehead Ferns -Niguro-', 'Fish', 'Garden Peas', 'Garden cress-Chamsur ko saag-', 'Garlic', 'Ginger', 
                       'Green Brinjal', 'Green Lentils', 'Green Mint -Pudina-', 'Green Peas', 'Green Soyabean -Hariyo Bhatmas-', 
                       'Gundruk', 'Ham', 'Ice', 'Jack Fruit', 'Ketchup', 'Lapsi -Nepali Hog Plum-', 'Lemon -Nimbu-', 
                       'Lime -Kagati-', 'Long Beans -Bodi-', 'Masyaura', 'Milk', 'Minced Meat', 
                       'Moringa Leaves -Sajyun ko Munta-', 'Mushroom', 'Mutton', 'Nutrela -Soya Chunks-', 'Okra -Bhindi-', 
                       'Olive Oil', 'Onion', 'Onion Leaves', 'Orange', 'Palak -Indian Spinach-', 'Palungo -Nepali Spinach-', 
                       'Paneer', 'Papaya', 'Pea', 'Pear', 'Pointed Gourd -Chuche Karela-', 'Pork', 'Potato', 'Pumpkin -Farsi-', 
                       'Radish', 'Rahar ko Daal', 'Rayo ko Saag', 'Red Beans', 'Red Lentils', 'Rice -Chamal-', 
                       'Sajjyun -Moringa Drumsticks-', 'Salt', 'Sausage', 'Snake Gourd -Chichindo-', 'Soy Sauce', 
                       'Soyabean -Bhatmas-', 'Sponge Gourd -Ghiraula-', 'Stinging Nettle -Sisnu-', 'Strawberry', 'Sugar', 
                       'Sweet Potato -Suthuni-', 'Taro Leaves -Karkalo-', 'Taro Root-Pidalu-', 'Thukpa Noodles', 'Tofu', 
                       'Tomato', 'Tori ko Saag', 'Tree Tomato -Rukh Tamatar-', 'Turnip', 'Wallnut', 'Water Melon', 'Wheat',
                       'Yellow Lentils', 'kimchi', 'mayonnaise', 'noodle', 'seaweed' }

    detected_allowed_objects = set()
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            cls_name = names[cls_id]
            if cls_name in allowed_objects:
                detected_allowed_objects.add(cls_name)

    # результат розпізнавання
    processed_images = glob.glob(os.path.join(temp_dir, "*.jpg"))
    if processed_images:
        processed_image = processed_images[0]
        st.image(processed_image, caption="🔍 Результат розпізнавання", use_container_width=True)
        shutil.copy(processed_image, os.path.join("saved_images/processed", f"{timestamp}.jpg"))

    st.markdown("## 🧾 Відредагуйте список інгредієнтів")
    ingredients_input = st.text_area("Інгредієнти (по одному в рядок)", value="\n".join(sorted(detected_allowed_objects)))
    ingredients = [i.strip().lower() for i in ingredients_input.split("\n") if i.strip()]

    if os.path.exists(image_path):
        os.remove(image_path)

    #  зберігання стану для рецептів
    if "translated_recipes" not in st.session_state:
        st.session_state.translated_recipes = []

if st.button("🔎 Знайти рецепти"):
    def parse_block(lines):
        try:
            title = lines[0].strip()
            ing = eval(lines[1].replace("INGREDIENTS:", "").strip())
            dir = eval(lines[2].replace("DIRECTIONS:", "").strip())
            return title, ing, dir
        except:
            return None

    recipes = []
    filepath = "recipes.txt"
    with open(filepath, "r", encoding="utf-8") as f:
        lines = []
        for line in f:
            if line.strip() == "":
                if len(lines) == 3:
                    parsed = parse_block(lines)
                    if parsed:
                        recipes.append(parsed)
                lines = []
            else:
                lines.append(line)

    scored = []
    for title, ing_list, dir in recipes:
        score = sum(1 for ing in ing_list if ing.lower() in ingredients)
        if score > 0:
            scored.append((score, title, ing_list, dir))

    scored.sort(reverse=True)

    # Збереження рецептів в сесію
    st.session_state.translated_recipes = []

    for score, title, ing_list, dir in scored[:3]:
        st.session_state.translated_recipes.append({
            "title": title,
            "ingredients": ing_list,
            "directions": dir
        })

# вибір мови
if "translated_recipes" in st.session_state and st.session_state.translated_recipes:
    lang = st.radio("🌐 Оберіть мову відображення рецептів:", ["Англійська", "Українська"])
    st.markdown("## 🍽 Відібрані рецепти")

    for recipe in st.session_state.translated_recipes:
        if lang == "Англійська":
            st.markdown(f"### 📝 {recipe['title']}")
            st.markdown("**Інгредієнти:**")
            st.markdown("\n".join([f"- {ing}" for ing in recipe["ingredients"]]))
            st.markdown("**Інструкція:**")
            st.markdown(" ".join(recipe["directions"]))
        else:
            if "title_uk" not in recipe:
                recipe["title_uk"] = translate_text(recipe["title"])
                recipe["ingredients_uk"] = [translate_text(ing) for ing in recipe["ingredients"]]
                recipe["directions_uk"] = translate_text(" ".join(recipe["directions"]))

            st.markdown(f"### 📝 {recipe['title_uk']}")
            st.markdown("**Інгредієнти:**")
            st.markdown("\n".join([f"- {ing}" for ing in recipe["ingredients_uk"]]))
            st.markdown("**Інструкція:**")
            st.markdown(recipe["directions_uk"])
