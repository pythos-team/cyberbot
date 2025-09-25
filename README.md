CyberBot

  

CyberBot — AI-powered automation and bot management SDK for developers.


---

🚀 Overview

CyberBot is a versatile AI-powered automation bot and SDK designed for developers and tech enthusiasts. It simplifies bot creation, automates repetitive tasks, and enables seamless API integration. With support for Python and JavaScript, CyberBot helps you manage workflows, monitor activity, and interact with servers effortlessly—all while keeping security and scalability in mind.


---

📦 Features

Create and manage automation bots with minimal setup

Easy API and server integration

Rate-limiting and IP management built-in

Works with Python and JavaScript

Lightweight and secure SDK

Open to customization and developer contributions



---

⚡ Installation

Python

pip install cyberbot

JavaScript / Node.js

npm install cyberbot /not realeased

> If using in the browser, include the SDK via script:



<script src="https://server-cdns-org.onrender.com/cdn/libs/cyberbot.js"></script>


---

🛠️ Usage

Python Example

from flask import Flask, render_template
from cyberbot import Bot
import time

app = Flask(__name__)

bot = Bot(app=app, api_key="PRO123", bot_env=True)
key = bot.generate_key()
bot.encrypt_app(key)
bot.keep_host_alive(url="http://127.0.0.1:8000", interval=60)

db_pass = bot.get_secret("DB_PASS")
@app.route("/")
def home():
    print(db_pass)
    return f"Hello World! data pass: {db_pass}"
    
@app.route("/wow")
def wow():
  return render_template("index.html")
    
@bot.lock_route("/test", password="Alextestbot")
def test():
    return "Hello"

# Run the Flask app
bot.run(port=5000)

Browser Example

browers sdk is used to decrept encrypted app

<script src="https://server-cdns-org.onrender.com/cdn/libs/cyberbot.js"></script>

<pre id="output" style="
  background:#111; 
  color:#0f0; 
  padding:1em; 
  border-radius:8px; 
  font-family:monospace; 
  white-space:pre-wrap; 
  word-break:break-word;
"></pre>

<script>
document.addEventListener("DOMContentLoaded", async () => {
  const bot = new CyberBot("P+HWD8MNddNY+aDSpTQHPzWfdgnVoLWWGhpJs4fOEKQ=");
  const out = document.getElementById("output");

  const data = await bot.fetch("http://127.0.0.1:5000/");

  if (data) {
    if (data.type === "text") {
      out.textContent = data.content;
    } else if (data.type === "html"){
      out.innerHTML = data.content;
    }
  }
});
</script>


---

📄 Documentation

Full API docs: https://github.com/pythos-team/cyberbot

Examples for Python, JS, and browser usage included in /examples folder



---

🤝 Contributing

We welcome contributions!

1. Fork the repository


2. Create a new branch (git checkout -b feature/your-feature)


3. Commit your changes (git commit -am 'Add feature')


4. Push to the branch (git push origin feature/your-feature)


5. Open a pull request




---

⚖️ License

This project is licensed under the MIT License — see the LICENSE file for details.

