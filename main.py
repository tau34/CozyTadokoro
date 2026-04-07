import discord
from discord.ext import commands
import sympy as sp
import matplotlib.pyplot as plt

bot = commands.Bot(command_prefix="!")

@bot.command()
async def tex(ctx):
  x = sp.Symbol('x')
  expr = sp.integrate(x**2, x)

  latex = sp.latex(expr)

  plt.text(0.5, 0.5, f"${latex}$", ha='center')
  plt.axis('off')
  plt.savefig("formula.png")

  await ctx.send(file=discord.File("formula.png"))

bot.run("TOKEN")