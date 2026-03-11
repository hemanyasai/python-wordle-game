from flask import Flask, render_template, request, redirect, url_for, session, flash
import random

app = Flask(__name__)
app.secret_key = 'a_super_secret_key'

WORDS = {
    4: ['code', 'palm', 'lava', 'rock'],
    5: ['water', 'brave', 'major', 'dream','magic','learn',],
    6: ['planet', 'bright', 'jumper', 'master']
}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/choose', methods=['GET', 'POST'])
def choose_length():
    if request.method == 'POST':
        try:
            length = int(request.form.get('word_length'))
            if length in WORDS:
                session['word_length'] = length
                session['secret_word'] = random.choice(WORDS[length])
                session['attempts'] = []
                session['max_attempts'] = length
                return redirect(url_for('game'))
            else:
                flash("Invalid word length selected!")
        except (ValueError, TypeError):
            flash("Invalid input. Please try again.")
    return render_template('choose.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    word_length = session.get('word_length')
    secret_word = session.get('secret_word')
    attempts = session.get('attempts', [])
    max_attempts = session.get('max_attempts', word_length)

    if not word_length or not secret_word:
        return redirect(url_for('choose_length'))

    error_message = None

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'quit':
            return redirect(url_for('home'))

        guess = request.form.get('guess', '').lower().strip()

        if len(attempts) >= max_attempts:
            session['result'] = 'lost'
            return redirect(url_for('result'))

        if len(guess) != word_length:
            error_message = f"Please enter a {word_length}-letter word."
        elif not guess.isalpha():
            error_message = "Please use only letters."
        else:
            feedback = ['grey'] * word_length
            secret_chars = list(secret_word)

            for i in range(word_length):
                if guess[i] == secret_word[i]:
                    feedback[i] = 'green'
                    secret_chars[i] = None

            for i in range(word_length):
                if feedback[i] != 'green' and guess[i] in secret_chars:
                    feedback[i] = 'yellow'
                    secret_chars[secret_chars.index(guess[i])] = None

            attempts.append({'guess': guess, 'feedback': feedback})
            session['attempts'] = attempts

            if guess == secret_word:
                session['result'] = 'won'
                return redirect(url_for('result'))

            if len(attempts) >= max_attempts:
                session['result'] = 'lost'
                return redirect(url_for('result'))

    return render_template('game.html', word_length=word_length, attempts=attempts, error=error_message)

@app.route('/result')
def result():
    result = session.get('result')
    secret_word = session.get('secret_word')
    return render_template('result.html', result=result, secret_word=secret_word)

@app.route('/new_game')
def new_game():
    session.clear()
    return redirect(url_for('choose_length'))

if __name__ == '__main__':
    app.run(debug=True)