import json
import requests

languages = ["en", "ja"]


def get_pokemon_specy(id: int) -> any:
    url = f"https://pokeapi.co/api/v2/pokemon-species/{id}"
    print(url)
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def get_data() -> list:
    data = []
    for id in range(1, 1050):
        pokemon_specy = get_pokemon_specy(id)
        if pokemon_specy is None:
            break
        for v in pokemon_specy["varieties"]:
            url = v["pokemon"]["url"]
            print(url)
            response = requests.get(url)
            if response.status_code == 200:
                pokemon = response.json()
                pokemon["names"] = [
                    {"language": e["language"]["name"], "name": e["name"]}
                    for e in pokemon_specy["names"]
                    if e["language"]["name"] in languages
                ]
                data.append(pokemon)
    return data


def get_pokemon_base_stat(pokemon, name: str) -> int:
    for stat in pokemon["stats"]:
        if stat["stat"]["name"] == name:
            return stat["base_stat"]
    return 0


def write_to_json(data: list, file_path: str):
    for obj in data:
        obj["abilities"] = sorted(e["ability"]["name"] for e in obj["abilities"])
        del obj["forms"]
        del obj["game_indices"]
        del obj["held_items"]
        del obj["is_default"]
        del obj["location_area_encounters"]
        for e in obj["moves"]:
            e["move"] = e["move"]["name"]
            for e2 in e["version_group_details"]:
                e2["move_learn_method"] = e2["move_learn_method"]["name"]
                e2["version_group"] = e2["version_group"]["name"]
        del obj["order"]
        del obj["past_abilities"]
        del obj["past_types"]
        obj["species"] = obj["species"]["name"]
        del obj["sprites"]
        obj["hp"] = get_pokemon_base_stat(obj, "hp")
        obj["attack"] = get_pokemon_base_stat(obj, "attack")
        obj["special-attack"] = get_pokemon_base_stat(obj, "special-attack")
        obj["defense"] = get_pokemon_base_stat(obj, "defense")
        obj["special-defense"] = get_pokemon_base_stat(obj, "special-defense")
        del obj["stats"]
        obj["types"] = sorted([e["type"]["name"] for e in obj["types"]])

    with open(file_path, mode="w", encoding="utf-8", newline="") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)


file_path = "data/pokemons.json"
data = get_data()
write_to_json(data, file_path)
