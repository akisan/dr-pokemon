# dr-pokemon

dr-pokemon は[ポケモンクイズ](https://quizgenerator.net/quizhoster/files/da570e40c908928e6c94eb1e7eaf812c/) を解くための Agent です。[PokéAPI](https://pokeapi.co/) のデータを使って回答します。

## Requirements

* Python 3.10+

## 使い方

.env ファイルに OPENAI_API_KEY を記入します。

```ini
OPENAI_API_KEY="<YOUR_OPENAI_API_KEY>"
```

venv による仮想環境を作成し、有効化します。

```bash
cd dr-pokemon
python3 -m venv .venv
source .venv/bin/activate
```

仮想環境にパッケージをインストールします。

```bash
(.venv) >python -m pip install -r requirements.txt
```

仮想環境で `main.py` を実行します。

```bash
(.venv) >python3 main.py
```

問題文を入力し、Enter キーを押すと質問に回答します。例えば:

```bash
問題を入力してください: ゴンベと同じ体重のポケモンは次のうちどれ？サナギラス, ゴローン, コドラ, ガントル


> Entering new AgentExecutor chain...

Invoking: `get_pokemon_info` with `{'pokemon_name': 'ゴンベ'}`


{'name': 'munchlax', 'abilities': ['gluttony', 'pickup', 'thick-fat'], 'hp': 135, 'attack': 85, 'special-attack': 40, 'defense': 40, 'special-defense': 85, 'types': ['normal'], 'weight': 1050}
Invoking: `get_pokemon_info` with `{'pokemon_name': 'サナギラス'}`


{'name': 'pupitar', 'abilities': ['shed-skin'], 'hp': 70, 'attack': 84, 'special-attack': 65, 'defense': 70, 'special-defense': 70, 'types': ['ground', 'rock'], 'weight': 1520}
Invoking: `get_pokemon_info` with `{'pokemon_name': 'ゴローン'}`


{'name': 'graveler', 'abilities': ['rock-head', 'sand-veil', 'sturdy'], 'hp': 55, 'attack': 95, 'special-attack': 45, 'defense': 115, 'special-defense': 45, 'types': ['ground', 'rock'], 'weight': 1050}
Invoking: `get_pokemon_info` with `{'pokemon_name': 'コドラ'}`


{'name': 'lairon', 'abilities': ['heavy-metal', 'rock-head', 'sturdy'], 'hp': 60, 'attack': 90, 'special-attack': 50, 'defense': 140, 'special-defense': 50, 'types': ['rock', 'steel'], 'weight': 1200}
Invoking: `get_pokemon_info` with `{'pokemon_name': 'ガントル'}`


{'name': 'boldore', 'abilities': ['sand-force', 'sturdy', 'weak-armor'], 'hp': 70, 'attack': 105, 'special-attack': 50, 'defense': 105, 'special-defense': 40, 'types': ['rock'], 'weight': 1020}ゴンベと同じ体重のポケモンは「ゴローン」です。

> Finished chain.
```
