from flask import Flask, render_template
from cyberbot import Bot
import time

app = Flask(__name__)

bot = Bot(app=app, api_key="PRO123", bot_env=True)
key = bot.generate_key()
bot.encrypt_app(key)

db_pass = bot.get_secret("DB_PASS")
@app.route("/")
def home():
    print(db_pass)
    return f"Hello World! data pass: {db_pass}"
    
@app.route("/wow")
def wow():
  return render_template("index.html")
    
@bot.lock_route("/test", password="Alex2002bot")
def test():
    return "Hello"

# Run the Flask app
bot.run(port=5000)