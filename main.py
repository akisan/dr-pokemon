import json
import math
from dotenv import load_dotenv
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.tools.render import format_tool_to_openai_function


def read_json_file(file_name: str) -> list[dict]:
    with open(file_name, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


abilities = read_json_file("data/abilities.json")
moves = read_json_file("data/moves.json")
pokemons = read_json_file("data/pokemons.json")
types = read_json_file("data/types.json")


def print_json(data):
    print(json.dumps(data, indent=2))


def calculate_damage(level: int, power: int, attack: int, defense: int) -> int:
    if level is None or power is None or attack is None or defense is None:
        return None

    # 攻撃側のレベル×2÷5+2→切り捨て
    damage = math.floor(level * 2 / 5 + 2)

    # ×物理技(特殊技)の威力×攻撃側のこうげき(とくこう)÷防御側のぼうぎょ(とくぼう)→切り捨て
    damage = math.floor(damage * power * attack / defense)

    # ÷50+2→切り捨て
    damage = math.floor(damage / 50 + 2)

    # 乱数(0.85, 0.86, …… ,0.99, 1.00 のどれか)→切り捨て
    return math.floor(damage * 1)


def calculate_stat(level: int, base: int, value: int, effort: int, seikaku: int) -> int:
    # 能力値＝{(種族値×2＋個体値＋努力値÷4)×レベル÷100＋5}×性格補正
    return math.floor(((base * 2 + value + effort / 4) * level / 100 + 5) * seikaku)


@tool
def calculate_pokemon_max_damage(
    pokemon_name_or_id: str,
    target_pokemon_name_or_id: str,
) -> int | None:
    """ポケモンに与える最大ダメージを計算します。

    :param pokemon_name_or_id: 攻撃するポケモンのIDまたは名前
    :param target_pokemon_name_or_id: 防御するポケモンのIDまたは名前
    :return: 最大ダメージ
    """
    pokemon = get_pokemon(pokemon_name_or_id)
    target_pokemon = get_pokemon(target_pokemon_name_or_id)
    if None in [pokemon, target_pokemon]:
        return None

    level = 50
    attack = calculate_stat(level, pokemon["attack"], 0, 0, 1)
    special_attack = calculate_stat(level, pokemon["special-attack"], 0, 0, 1)
    defense = calculate_stat(level, pokemon["defense"], 0, 0, 1)
    special_defense = calculate_stat(level, pokemon["special-defense"], 0, 0, 1)
    max_damage = 0
    for pokemon_move in pokemon["name"]:
        move = get_move(pokemon_move["move"])
        if move is None:
            continue

        damage_class = move["damage_class"]
        power = move["power"]
        if damage_class == "status" or power is None:
            continue

        if damage_class == "physical":
            max_damage = max(
                max_damage, calculate_damage(level, power, attack, defense)
            )
        elif damage_class == "special":
            max_damage = max(
                max_damage,
                calculate_damage(level, power, special_attack, special_defense),
            )

    return max_damage


def get_ability(ability_name: str) -> dict | None:
    """特性の情報を取得する。

    :param ability_name: 特性の名前
    :return: 特性の情報
    """
    ability_name = ability_name.upper()
    for ability in abilities:
        for name in ability["names"]:
            if name["name"].upper() == ability_name:
                return ability
    return None


def get_move(move_name: str) -> dict | None:
    """技の情報を取得する。

    :param move_name_or_id: 技の名前
    :return: 技の情報
    """
    move_name = move_name.upper()
    for move in moves:
        for name in move["names"]:
            if name["name"].upper() == move_name:
                return move
    return None


def get_pokemon(pokemon_name: str) -> dict | None:
    """ポケモンの情報を取得する。

    :param pokemon_name: ポケモンの名前
    :return: ポケモンの情報
    """
    pokemon_name = pokemon_name.upper()
    is_mega = pokemon_name.startswith("メガ")
    if is_mega:
        pokemon_name = pokemon_name[2:]

    for pokemon in pokemons:
        for name in pokemon["names"]:
            if name["name"].upper() == pokemon_name:
                if is_mega:
                    pokemon_mega_name = pokemon["name"] + "-mega"
                    for pokemon_mega in pokemons:
                        if pokemon_mega["name"] == pokemon_mega_name:
                            return pokemon_mega
                    return None
                else:
                    return pokemon
    return None


@tool
def get_pokemon_info(pokemon_name: str) -> dict | None:
    """ポケモンの情報を取得する。

    :param pokemon_name_or_id: ポケモンの名前
    :return: ポケモンの情報
    """
    pokemon = get_pokemon(pokemon_name)
    if pokemon is None:
        return None

    return {
        "name": pokemon["name"],
        "abilities": pokemon["abilities"],
        "hp": pokemon["hp"],
        "attack": pokemon["attack"],
        "special-attack": pokemon["special-attack"],
        "defense": pokemon["defense"],
        "special-defense": pokemon["special-defense"],
        "types": pokemon["types"],
        "weight": pokemon["weight"],
    }


def get_type(type_name: str) -> dict | None:
    """ポケモンと技のタイプの情報を取得する。

    :param type_name: タイプの名前
    :return: タイプの情報
    """
    type_name = type_name.upper()
    for type in types:
        for name in type["names"]:
            if name["name"].upper() == type_name:
                return type
    return None


@tool
def is_reproducible_combination(pokemon_name: str, combination_name: str) -> bool:
    """再現可能な組み合わせであるかを判定します。

    :param pokemon_name: ポケモンの名前
    :param combination_name: 組み合わせる技・特性・技タイプの名前
    :return: 再現可能な組み合わせであるかを返します。
    """
    pokemon = get_pokemon(pokemon_name)
    if pokemon is None:
        print("pokemon not found")
        return False

    print(f'pokemon: {pokemon["name"]}')

    move = get_move(combination_name)
    if move is not None:
        print(f'move: {move["name"]}')
        for pokemon_move in pokemon["moves"]:
            if pokemon_move["move"] == move["name"]:
                # for d in pokemon_move["version_group_details"]:
                #     if any(d["move_learn_method"] in ["egg", "level-up"]):
                print_json(pokemon_move)
                return True
        return False

    ability = get_ability(combination_name)
    if ability is not None:
        print(f'ability: {ability["name"]}')
        if ability["name"] in pokemon["abilities"]:
            print(pokemon["abilities"])
            return True
        return False

    type = get_type(combination_name)
    if type is not None:
        print(f'type: {type["name"]}')
        for pokemon_move in pokemon["moves"]:
            move = get_move(pokemon_move["move"])
            if move is None:
                continue
            print(f'move: {move["name"]}({move["type"]})')
            if move["type"] == type["name"]:
                print_json(move)
                return True
        return False

    return False


load_dotenv()

tools = [
    calculate_pokemon_max_damage,
    get_pokemon_info,
    is_reproducible_combination,
]

llm = ChatOpenAI(model="gpt-4", temperature=0)
llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

MEMORY_KEY = "chat_history"
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """次の問題に答えてください。
ツールを使用して問題に答えてください。

ファンの間では、それぞれの能力のことをアルファベット(英語)で省略表記することがあります。

H: HP
A: こうげき
B: ぼうぎょ
C: とくこう
D: とくぼう
S: すばやさ

「H-A-B-C-D-S」の順で、数値のみをハイフンで繋げて表記することも多い。

問題: """,
        ),
        MessagesPlaceholder(variable_name=MEMORY_KEY),
        (
            "user",
            """{input}""",
        ),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)


chat_history = []

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: x["chat_history"],
    }
    | prompt
    | llm_with_tools
    | OpenAIFunctionsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

while True:
    question = input("問題を入力してください: ")
    result = agent_executor.invoke({"input": question, "chat_history": chat_history})
    # chat_history.extend(
    #     [
    #         HumanMessage(content=question),
    #         AIMessage(content=result["output"]),
    #     ]
    # )
