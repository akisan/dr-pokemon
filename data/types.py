import json
import requests

languages = ["en", "ja"]


def get_data() -> list:
    data = []
    for id in range(1, 20):
        url = f"https://pokeapi.co/api/v2/type/{id}"
        print(url)
        response = requests.get(url)
        if response.status_code == 200:
            data.append(response.json())
        else:
            break
    return data


def write_to_json(data: list, file_path: str):
    for obj in data:
        del obj["damage_relations"]
        del obj["game_indices"]
        del obj["generation"]
        if obj["move_damage_class"] is not None:
            obj["move_damage_class"] = obj["move_damage_class"]["name"]
        del obj["moves"]
        obj["names"] = [
            {"language": e["language"]["name"], "name": e["name"]}
            for e in obj["names"]
            if e["language"]["name"] in languages
        ]
        del obj["past_damage_relations"]
        del obj["pokemon"]

    with open(file_path, mode="w", encoding="utf-8", newline="") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)


file_path = "data/types.json"
data = get_data()
write_to_json(data, file_path)
