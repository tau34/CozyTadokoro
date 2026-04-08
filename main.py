import discord
from discord.ext import commands
import sympy as sp
import matplotlib.pyplot as plt
from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ===== Discord bot =====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
async def tex(ctx, *, formula):
    try:
        expr = sp.sympify(formula)
        latex = sp.latex(expr)

        plt.figure()
        plt.text(0.5, 0.5, f"${latex}$", ha='center')
        plt.axis('off')
        plt.savefig("formula.png")
        plt.close()

        await ctx.send(file=discord.File("formula.png"))

    except Exception as e:
        await ctx.send(f"Error: {e}")

token = os.environ.get("TOKEN")
print("TOKEN:", token)
print("LENGTH:", len(token) if token else "None")

keep_alive()
bot.run(os.environ["TOKEN"])
