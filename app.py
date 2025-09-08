from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import random
import string
from collections import Counter

app = Flask(__name__)
app.secret_key = 'dev'

leaderboard = {}

# Load word list
with open("words.txt") as f:
    DICTIONARY = set(word.strip().lower() for word in f)

def update_leaderboard(name, score):
    # If the player is new, or beats their own score
    if name not in leaderboard or score > leaderboard[name]:
        leaderboard[name] = score

def generate_letters():
    # uses approximate English letter frequencies for better distribution
    letters = list(string.ascii_lowercase)
    weights = [
        12.7,  # a
        1.5,   # b
        2.8,   # c
        4.3,   # d
        12.7,  # e
        2.2,   # f
        2.0,   # g
        6.1,   # h
        7.0,   # i
        0.2,   # j
        0.8,   # k
        4.0,   # l
        2.4,   # m
        6.7,   # n
        7.5,   # o
        1.9,   # p
        0.1,   # q
        6.0,   # r
        6.3,   # s
        9.1,   # t
        2.8,   # u
        1.0,   # v
        2.4,   # w
        0.2,   # x
        2.0,   # y
        0.1    # z
    ]

    return random.choices(letters, weights=weights, k=12)


def is_valid_word(word, available_letters):
    # checks that the word can be made from available letters and that the word is in the dictionary
    word_count = Counter(word.lower())
    letter_count = Counter(available_letters)
    for letter in word_count:
        if word_count[letter] > letter_count.get(letter, 0):
            return False
    return word.lower() in DICTIONARY

def calculate_score(word):
    score = 0
    vowels = "aeiou"
    three_pointers = "wkvyj"
    four_pointers = "zxq"

    for letter in word.lower():
        if letter in vowels:
            score += 1
        elif letter in three_pointers:
            score += 3
        elif letter in four_pointers:
            score += 4
        else:
            score += 2

    return score

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("player_name")
        if name:
            session['name'] = name
            return redirect(url_for("game"))
    return render_template("index.html")

@app.route("/game")
def game():
    name = session.get('name')
    if not name:
        return redirect(url_for('index'))
    return render_template("game.html", name=name)


@app.route("/get-letters")
def get_letters():
    letters = generate_letters()
    return jsonify({"letters": letters})

@app.route("/check-word", methods=["POST"])
def check_word():
    data = request.get_json()
    word = data["word"]
    letters = data["letters"]
    if not is_valid_word(word, letters):
        return jsonify({"valid": False, "score": 0})
    score = calculate_score(word)
    name = session.get("name")
    update_leaderboard(name, score)

    return jsonify({"valid": True, "score": score})

@app.route("/check_leaderboard", methods=["POST"])
def check_leaderboard():
    # sorts the leaderboard before showing it
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    return render_template("leaderboard.html", leaderboard=sorted_leaderboard)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
