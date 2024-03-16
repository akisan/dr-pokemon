import json
import os
import requests

languages = ["en", "ja"]


def get_data() -> list:
    data = []
    for id in range(1, 320):
        url = f"https://pokeapi.co/api/v2/ability/{id}"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            data.append(response.json())
        else:
            break
    return data


def write_to_json(data: list, file_path: str):
    for obj in data:
        del obj["effect_changes"]
        del obj["effect_entries"]
        del obj["flavor_text_entries"]
        del obj["generation"]
        del obj["is_main_series"]
        obj["names"] = [
            {"language": e["language"]["name"], "name": e["name"]}
            for e in obj["names"]
            if e["language"]["name"] in languages
        ]
        del obj["pokemon"]

    with open(file_path, mode="w", encoding="utf-8", newline="") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)


file_path = os.path.join(os.path.dirname(__file__), "../data/abilities.json")
data = get_data()
write_to_json(data, file_path)
