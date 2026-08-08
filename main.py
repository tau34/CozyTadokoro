import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import describe
import multiprocessing
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from flask import Flask
from threading import Thread
import os
import re
import MeCab
import unicodedata

mecab = MeCab.Tagger()

app = Flask('')

# ===== Discord bot =====
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

TIMEOUT_MSG = "処理時間の制限を超えました…\nアップグレードするには、https://www.patreon.com/c/tau34 で寄付してください！\n詳細はコマンド```/donate-infoで確認できます。```"

@app.route('/')
def home():
    return "I'm alive"

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await tree.sync()

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

def render_formula(latex, textColor, bgColor):
    plt.rcParams["mathtext.fontset"] = "stix"
    plt.rcParams["font.family"] = "STIXGeneral"

    fig = plt.figure(figsize=(4, 2), facecolor=bgColor if bgColor != "transparent" else None)
    ax = fig.add_subplot(111)

    ax.axis('off')

    fontsize = 50  # まずは大きく

    length = len(latex)
    if (length > 300):
        fontsize = 4

    text = ax.text(0.5, 0.5, f"${latex}$",
        ha='center', va='center',
        fontsize=fontsize, color=textColor)

    fig.canvas.draw()

    renderer = fig.canvas.get_renderer()
    bbox = text.get_window_extent(renderer=renderer)
    fig_width, fig_height = fig.canvas.get_width_height()

    while (bbox.width > fig_width * 0.9 or bbox.height > fig_height * 0.9) and fontsize > 5:
        fontsize -= 2
        text.set_fontsize(fontsize)
        fig.canvas.draw()
        bbox = text.get_window_extent(renderer=renderer)

    plt.savefig("formula.png", bbox_inches='tight', dpi=300, transparent=(bgColor == "transparent"))
    plt.close()

def latex_to_text(latex: str) -> str:
    latex = latex + " "

    replaces = [("digamma","\u03dd"),("varkappa","\u03f0"),("varGamma","\u0393"),("varDelta","\u0394"),("varTheta","\u0398"),("varLambda","\u039b"),("varXi","\u039e"),("varPi","\u03a0"),("varSigma","\u03a3"),("varUpsilon","\u03a5"),("varPhi","\u03a6"),("varPsi","\u03a8"),("varOmega","\u03a9"),("beth","\u2136"),("gimel","\u2137"),("daleth","\u2138"),("backprime","\u2035"),("hslash","\u210f"),("varnothing","\u2205"),("blacktriangle","\u25b4"),("triangledown","\u25bd"),("blacktriangledown","\u25be"),("square","\u25fb"),("Box","\u25fb"),("blacksquare","\u25fc"),("lozenge","\u25ca"),("Diamond","\u25ca"),("blacklozenge","\u29eb"),("circledS","\u24c8"),("bigstar","\u2605"),("sphericalangle","\u2222"),("measuredangle","\u2221"),("nexists","\u2204"),("complement","\u2201"),("mho","\u2127"),("eth","\xf0"),("Finv","\u2132"),("diagup","\u2571"),("Game","\u2141"),("diagdown","\u2572"),("yen","\xa5"),("circledR","\xae"),("checkmark","\u2713"),("maltese","\u2720"),("dotplus","\u2214"),("ltimes","\u22c9"),("smallsetminus","\u2216"),("rtimes","\u22ca"),("Cap","\u22d2"),("doublecap","\u22d2"),("leftthreetimes","\u22cb"),("Cup","\u22d3"),("doublecup","\u22d3"),("rightthreetimes","\u22cc"),("barwedge","\u22bc"),("curlywedge","\u22cf"),("veebar","\u22bb"),("curlyvee","\u22ce"),("doublebarwedge","\u2a5e"),("boxminus","\u229f"),("circleddash","\u229d"),("boxtimes","\u22a0"),("circledast","\u229b"),("boxdot","\u22a1"),("circledcirc","\u229a"),("boxplus","\u229e"),("centerdot","\u22c5"),("divideontimes","\u22c7"),("intercal","\u22ba"),("leqq","\u2266"),("geqq","\u2267"),("leqslant","\u2a7d"),("geqslant","\u2a7e"),("eqslantless","\u2a95"),("eqslantgtr","\u2a96"),("lesssim","\u2272"),("gtrsim","\u2273"),("lessapprox","\u2a85"),("gtrapprox","\u2a86"),("approxeq","\u224a"),("lessdot","\u22d6"),("gtrdot","\u22d7"),("lll","\u22d8"),("llless","\u22d8"),("ggg","\u22d9"),("gggtr","\u22d9"),("lessgtr","\u2276"),("gtrless","\u2277"),("lesseqgtr","\u22da"),("gtreqless","\u22db"),("lesseqqgtr","\u2a8b"),("gtreqqless","\u2a8c"),("doteqdot","\u2251"),("Doteq","\u2251"),("eqcirc","\u2256"),("risingdotseq","\u2253"),("circeq","\u2257"),("fallingdotseq","\u2252"),("triangleq","\u225c"),("backsim","\u223d"),("thicksim","\u223c"),("backsimeq","\u22cd"),("thickapprox","\u2248"),("subseteqq","\u2ac5"),("supseteqq","\u2ac6"),("Subset","\u22d0"),("Supset","\u22d1"),("sqsubset","\u228f"),("sqsupset","\u2290"),("preccurlyeq","\u227c"),("succcurlyeq","\u227d"),("curlyeqprec","\u22de"),("curlyeqsucc","\u22df"),("precsim","\u227e"),("succsim","\u227f"),("precapprox","\u2ab7"),("succapprox","\u2ab8"),("vartriangleleft","\u22b2"),("lhd","\u22b2"),("vartriangleright","\u22b3"),("rhd","\u22b3"),("trianglelefteq","\u22b4"),("unlhd","\u22b4"),("trianglerighteq","\u22b5"),("unrhd","\u22b5"),("vDash","\u22a8"),("Vdash","\u22a9"),("Vvdash","\u22aa"),("smallsmile","\u2323"),("shortmid","\u2223"),("smallfrown","\u2322"),("shortparallel","\u2225"),("bumpeq","\u224f"),("between","\u226c"),("Bumpeq","\u224e"),("pitchfork","\u22d4"),("varpropto","\u221d"),("backepsilon","\u220d"),("blacktriangleleft","\u25c2"),("blacktriangleright","\u25b8"),("therefore","\u2234"),("because","\u2235"),("eqsim","\u2242"),("vartriangle","\u25b3"),("Join","\u22c8"),("nless","\u226e"),("ngtr","\u226f"),("nleq","\u2270"),("ngeq","\u2271"),("nleqslant","\u2a87"),("ngeqslant","\u2a88"),("nleqq","\u2270"),("ngeqq","\u2271"),("lneq","\u2a87"),("gneq","\u2a88"),("lneqq","\u2268"),("gneqq","\u2269"),("lvertneqq","\u2268"),("gvertneqq","\u2269"),("lnsim","\u22e6"),("gnsim","\u22e7"),("lnapprox","\u2a89"),("gnapprox","\u2a8a"),("nprec","\u2280"),("nsucc","\u2281"),("npreceq","\u22e0"),("nsucceq","\u22e1"),("precneqq","\u2ab5"),("succneqq","\u2ab6"),("precnsim","\u22e8"),("succnsim","\u22e9"),("precnapprox","\u2ab9"),("succnapprox","\u2aba"),("nsim","\u2241"),("ncong","\u2247"),("nshortmid","\u2224"),("nshortparallel","\u2226"),("nmid","\u2224"),("nparallel","\u2226"),("nvdash","\u22ac"),("nvDash","\u22ad"),("nVdash","\u22ae"),("nVDash","\u22af"),("ntriangleleft","\u22ea"),("ntriangleright","\u22eb"),("ntrianglelefteq","\u22ec"),("ntrianglerighteq","\u22ed"),("nsubseteq","\u2288"),("nsupseteq","\u2289"),("nsubseteqq","\u2288"),("nsupseteqq","\u2289"),("subsetneq","\u228a"),("supsetneq","\u228b"),("varsubsetneq","\u228a"),("varsupsetneq","\u228b"),("subsetneqq","\u2acb"),("supsetneqq","\u2acc"),("varsubsetneqq","\u2acb"),("varsupsetneqq","\u2acc"),("leftleftarrows","\u21c7"),("rightrightarrows","\u21c9"),("leftrightarrows","\u21c6"),("rightleftarrows","\u21c4"),("Lleftarrow","\u21da"),("Rrightarrow","\u21db"),("twoheadleftarrow","\u219e"),("twoheadrightarrow","\u21a0"),("leftarrowtail","\u21a2"),("rightarrowtail","\u21a3"),("looparrowleft","\u21ab"),("looparrowright","\u21ac"),("leftrightharpoons","\u21cb"),("rightleftharpoons","\u21cc"),("curvearrowleft","\u21b6"),("curvearrowright","\u21b7"),("circlearrowleft","\u21ba"),("circlearrowright","\u21bb"),("Lsh","\u21b0"),("Rsh","\u21b1"),("upuparrows","\u21c8"),("downdownarrows","\u21ca"),("upharpoonleft","\u21bf"),("upharpoonright","\u21be"),("downharpoonleft","\u21c3"),("restriction","\u21be"),("multimap","\u22b8"),("downharpoonright","\u21c2"),("leftrightsquigarrow","\u21ad"),("rightsquigarrow","\u21dd"),("leadsto","\u21dd"),("dashrightarrow","\u21e2"),("dashleftarrow","\u21e0"),("nleftarrow","\u219a"),("nrightarrow","\u219b"),("nLeftarrow","\u21cd"),("nRightarrow","\u21cf"),("nleftrightarrow","\u21ae"),("nLeftrightarrow","\u21ce"),("alpha","α"),("beta","β"),("gamma","γ"),("delta","δ"),("epsilon","ϵ"),("zeta","ζ"),("eta","η"),("theta","θ"),("iota","ι"),("kappa","κ"),("lambda","λ"),("mu","μ"),("nu","ν"),("xi","ξ"),("omicron","ο"),("pi","π"),("rho","ρ"),("sigma","σ"),("tau","τ"),("upsilon","υ"),("phi","ϕ"),("chi","χ"),("psi","ψ"),("omega","ω"),("varepsilon","ε"),("vartheta","ϑ"),("varpi","ϖ"),("varrho","ϱ"),("varsigma","ς"),("varphi","φ"),("S","§"),("aleph","ℵ"),("hbar","ℏ"),("imath","\v1"),("jmath","ȷ"),("ell","ℓ"),("wp","℘"),("Re","ℜ"),("Im","ℑ"),("partial","∂"),("infty","∞"),("prime","′"),("emptyset","∅"),("nabla","∇"),("top","⊤"),("bot","⊥"),("angle","∠"),("triangle","△"),("backslash","∖"),("forall","∀"),("exists","∃"),("neg","¬"),("lnot","¬"),("flat","♭"),("natural","♮"),("sharp","♯"),("clubsuit","♣"),("diamondsuit","♢"),("heartsuit","♡"),("spadesuit","♠"),("surd","√"),("coprod","∐"),("bigvee","⋁"),("bigwedge","⋀"),("biguplus","⨄"),("bigcap","⋂"),("bigcup","⋃"),("int","∫"),("intop","∫"),("iint","∬"),("iiint","∭"),("prod","∏"),("sum","∑"),("bigotimes","⨂"),("bigoplus","⨁"),("bigodot","⨀"),("oint","∮"),("bigsqcup","⨆"),("smallint","∫"),("triangleleft","◃"),("triangleright","▹"),("bigtriangleup","△"),("bigtriangledown","▽"),("wedge","∧"),("land","∧"),("vee","∨"),("lor","∨"),("cap","∩"),("cup","∪"),("ddagger","‡"),("dagger","†"),("sqcap","⊓"),("sqcup","⊔"),("uplus","⊎"),("amalg","⨿"),("diamond","⋄"),("bullet","∙"),("wr","≀"),("div","÷"),("divsymbol","÷"),("odot","⊙"),("oslash","⊘"),("otimes","⊗"),("ominus","⊖"),("oplus","⊕"),("mp","∓"),("pm","±"),("circ","∘"),("bigcirc","◯"),("setminus","∖"),("cdot","⋅"),("ast","∗"),("times","×"),("star","⋆"),("propto","∝"),("sqsubseteq","⊑"),("sqsupseteq","⊒"),("parallel","∥"),("mid","∣"),("dashv","⊣"),("vdash","⊢"),("leq","≤"),("le","≤"),("geq","≥"),("ge","≥"),("lt","<"),("gt",">"),("succ","≻"),("prec","≺"),("approx","≈"),("succeq","⪰"),("preceq","⪯"),("supset","⊃"),("subset","⊂"),("supseteq","⊇"),("subseteq","⊆"),("in","∈"),("ni","∋"),("notin","∉"),("owns","∋"),("gg","≫"),("ll","≪"),("sim","∼"),("simeq","≃"),("perp","⊥"),("equiv","≡"),("asymp","≍"),("smile","⌣"),("frown","⌢"),("ne","≠"),("neq","≠"),("cong","≅"),("doteq","≐"),("bowtie","⋈"),("models","⊨"),("notChar","⧸"),("Leftrightarrow","⇔"),("Leftarrow","⇐"),("Rightarrow","⇒"),("leftrightarrow","↔"),("leftarrow","←"),("gets","←"),("rightarrow","→"),("to","→"),("mapsto","↦"),("leftharpoonup","↼"),("leftharpoondown","↽"),("rightharpoonup","⇀"),("rightharpoondown","⇁"),("nearrow","↗"),("searrow","↘"),("nwarrow","↖"),("swarrow","↙"),("rightleftharpoons","⇌"),("hookrightarrow","↪"),("hookleftarrow","↩"),("longleftarrow","⟵"),("Longleftarrow","⟸"),("longrightarrow","⟶"),("Longrightarrow","⟹"),("Longleftrightarrow","⟺"),("longleftrightarrow","⟷"),("longmapsto","⟼"),("ldots","…"),("cdots","⋯"),("vdots","⋮"),("ddots","⋱"),("dotsc","…"),("dotsb","⋯"),("dotsm","⋯"),("dotsi","⋯"),("dotso","…"),("ldotp","."),("cdotp","⋅"),("colon",":"),("Gamma","Γ"),("Delta","Δ"),("Theta","Θ"),("Lambda","Λ"),("Xi","Ξ"),("Pi","Π"),("Sigma","Σ"),("Upsilon","Υ"),("Phi","Φ"),("Psi","Ψ"),("Omega","Ω"),("_","_"),("#","#"),("$","$"),("%","%"),("&","&"),("And","&"),("(","("),(")",")"),("[","["),("]","]"),("<","⟨"),(">","⟩"),("\\lt","⟨"),("\\gt","⟩"),("/","/"),("|","|"),(".",""),("\\\\","\\"),("\\lmoustache","⎰"),("\\rmoustache","⎱"),("\\lgroup","⟮"),("\\rgroup","⟯"),("\\arrowvert","⏐"),("\\Arrowvert","‖"),("\\bracevert","⎪"),("\\Vert","‖"),("\\|","‖"),("\\vert","|"),("\\uparrow","↑"),("\\downarrow","↓"),("\\updownarrow","↕"),("\\Uparrow","⇑"),("\\Downarrow","⇓"),("\\Updownarrow","⇕"),("\\backslash","\\"),("\\rangle","⟩"),("\\langle","⟨"),("\\rbrace","}"),("\\lbrace","{"),("\\}","}"),("\\{","{"),("\\rceil","⌉"),("\\lceil","⌈"),("\\rfloor","⌋"),("\\lfloor","⌊")]

    latex = re.sub(r'\\int_{(.*?)}\^{(.*?)} ', r'∫[\1→\2] ', latex)
    latex = re.sub(r'\\int_(.*?)\^{(.*?)} ', r'∫[\1→\2] ', latex)
    latex = re.sub(r'\\int_{(.*?)}\^(.*?) ', r'∫[\1→\2] ', latex)
    latex = re.sub(r'\\int_(.*?)\^(.*?) ', r'∫[\1→\2] ', latex)

    latex = re.sub(r'\\sum_{(.*?)=(.*?)}\^{(.*?)} ', r'Σ[\1=\2→\3] ', latex)
    latex = re.sub(r'\\sum_(.*?)=(.*?)\^{(.*?)} ', r'Σ[\1=\2→\3] ', latex)
    latex = re.sub(r'\\sum_{(.*?)=(.*?)}\^(.*?) ', r'Σ[\1=\2→\3] ', latex)
    latex = re.sub(r'\\sum_(.*?)=(.*?)\^(.*?) ', r'Σ[\1=\2→\3] ', latex)
    
    latex = re.sub(r'\\prod_{(.*?)=(.*?)}\^{(.*?)} ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\prod_(.*?)=(.*?)\^{(.*?)} ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\prod_{(.*?)=(.*?)}\^(.*?) ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\prod_(.*?)=(.*?)\^(.*?) ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\bigtimes_{(.*?)=(.*?)}\^{(.*?)} ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\bigtimes_(.*?)=(.*?)\^{(.*?)} ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\bigtimes_{(.*?)=(.*?)}\^(.*?) ', r'∏[\1=\2→\3] ', latex)
    latex = re.sub(r'\\bigtimes_(.*?)=(.*?)\^(.*?) ', r'∏[\1=\2→\3] ', latex)

    latex = re.sub(r'\\frac{(.*?)}{(.*?)}', r'((\1) / (\2))', latex)

    latex = re.sub(r' \^{(.*?)}', r' ^ (\1)', latex)
    latex = re.sub(r' \^(.*?)', r' ^ \1', latex)
    latex = re.sub(r'\^{(.*?)}', r' ^ (\1)', latex)
    latex = re.sub(r'\^(.*?)', r' ^ \1', latex)

    latex = re.sub(r' _{(.*?)}', r' _(\1)', latex)
    latex = re.sub(r' _(.*?)', r' _\1', latex)
    latex = re.sub(r'_{(.*?)}', r'_(\1)', latex)
    latex = re.sub(r'_(.*?)', r'_\1', latex)

    latex = latex.replace(r' \cdot ', ' * ')
    latex = latex.replace(r'\cdot ', '* ')
    latex = latex.replace(r' \cdot', ' *')
    latex = latex.replace(r'\cdot', '*')
    latex = latex.replace(r' \times ', ' * ')
    latex = latex.replace(r'\times ', '* ')
    latex = latex.replace(r' \times', ' *')
    latex = latex.replace(r'\times', '*')

    latex = re.sub(r'\\sqrt{(.*?)}', r'√(\1)', latex)
    latex = re.sub(r'\\sqrt(.*?)', r'√\1', latex)

    for old, new in replaces:
        latex = latex.replace('\\' + old + ' ', new)

    latex = latex.rstrip(" ")

    return latex


def is_emoji_or_symbol(text):
    for ch in text:
        category = unicodedata.category(ch)

        if category in ("So", "Sk"):
            return True

    return False

def should_keep(surface, features):
    pos = features[0]

    if pos == "補助記号":
        return True

    if pos == "未知語":
        return True

    if is_emoji_or_symbol(surface):
        return True

    return False

def replace_with_pos(text, detailed):
    result = []

    node = mecab.parseToNode(text)

    while node:
        surface = node.surface
        feature = node.feature

        if not surface:
            node = node.next
            continue

        features = feature.split(",")

        CONNCECT_LIST = ["動詞", "形容詞", "形状詞", "接尾辞"]
        if should_keep(surface, features):
            result.append(surface)
        elif features[0] == "代名詞":
            if detailed:
                result.append("代名詞")
            else:
                result.append("名詞")
        elif (not detailed) or features[1] == "*":
            result.append(features[0])
        elif features[0] in CONNCECT_LIST:
            result.append(f"{features[1]}{features[0]}")
        elif features[0] == "感動詞":
            if features[1] == "フィラー":
                result.append("フィラー")
            else:
                result.append("一般感動詞")
        else:
            result.append(features[1])

        if detailed and features[2] != "*":
            if detailed and features[3] != "*":
                result.append(f"({features[2]}、{features[3]})")
            else:
                result.append(f"({features[2]})")

        node = node.next

    return "".join(result)

def analyze_text(text, detailed):
    parts = text.split(" ")
    for i in range(len(parts)):
        s = parts[i]
        s1 = s.split("　")
        for j in range(len(s1)):
            s2 = s1[j]
            s3 = s2.split("\n")
            s3 = [replace_with_pos(x, detailed) for x in s3]
            s1[j] = "\n".join(s3)
        parts[i] = "　".join(s1)

    return " ".join(parts).replace("形状詞助動詞", "形容動詞").replace("形状詞可能", "形容動詞可能")


def _render_formula_worker(formula, text_color, bg_color, result_queue):
    try:
        render_formula(formula, textColor=text_color, bgColor=bg_color)
        result_queue.put(("ok", None))
    except Exception as exc:
        result_queue.put(("error", str(exc)))


def _analyze_text_worker(text, detailed, result_queue):
    try:
        result_queue.put(("ok", analyze_text(text, detailed)))
    except Exception as exc:
        result_queue.put(("error", str(exc)))


def run_with_timeout(target, args, timeout_seconds):
    result_queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=target, args=(*args, result_queue))

    process.start()
    process.join(timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        return ("timeout", None)

    try:
        return result_queue.get(timeout=1)
    except Exception:
        return ("error", "結果を取得できませんでした")

@tree.command(name="tex", description="数式を画像で表示")
@describe(
    formula="数式のTeXコード",
    text_color="文字色",
    bg_color="背景色"
)
async def tex(interaction: discord.Interaction,
                formula: str, text_color: str = "black", bg_color: str = "white"):
    await interaction.response.defer()

    status, payload = run_with_timeout(
        _render_formula_worker,
        (formula, text_color, bg_color),
        10,
    )

    if status == "timeout":
        await interaction.followup.send(TIMEOUT_MSG)
        return

    if status == "ok":
        await interaction.followup.send(file=discord.File("formula.png"))
    else:
        await interaction.followup.send(f"Error: {payload}")

@tree.command(name="tex-text", description="数式をテキスト表示")
@describe(formula="数式のTeXコード")
async def tex_text(interaction: discord.Interaction, formula: str):
    try:
        await interaction.response.send_message(latex_to_text(formula))

    except Exception as e:
        await interaction.response.send_message(f"Error: {e}")

@tree.command(name="analyze", description="日本語の文章を品詞分解")
@describe(text="品詞分解する文章", detailed="詳細表示するか否か。する:True、しない(デフォルト):False")
async def analyze(interaction: discord.Interaction, text: str, detailed: bool = False):
    await interaction.response.defer()

    status, payload = run_with_timeout(
        _analyze_text_worker, (text, detailed), 10)

    if status == "timeout":
        await interaction.followup.send(TIMEOUT_MSG)
        return

    if status == "ok":
        await interaction.followup.send(payload)
        return

    if status == "error":
        await interaction.followup.send(f"Error: {payload}")

@tree.command(name="donate-info", description="寄付の情報を表示")
async def donate_info(interaction: discord.Interaction):
    await interaction.response.send_message(
        "このBotは、寄付によって運営されています。\n"
        "寄付額が一定の金額を超えると、より多くの機能やサポートを提供することができます。\n"
        "寄付は以下のリンクから行うことができます。\n"
        "https://www.patreon.com/c/tau34\n"
    )

@tree.context_menu(name="品詞分解")
async def analyze_message(interaction: discord.Interaction, message: discord.Message):
    content = message.content

    if not content:
        await interaction.response.send_message("このメッセージにはテキストが含まれていません。", ephemeral=True)
        return

    await interaction.response.defer()

    status, payload = run_with_timeout(
        _analyze_text_worker, (content, False), 10)

    if status == "timeout":
        await interaction.followup.send(TIMEOUT_MSG)
        return

    if status == "ok":
        await interaction.followup.send(payload)
        return

    if status == "error":
        await interaction.followup.send(f"Error: {payload}")

@tree.context_menu(name="品詞分解(詳細表示)")
async def analyze_message_detailed(interaction: discord.Interaction, message: discord.Message):
    content = message.content

    if not content:
        await interaction.response.send_message("このメッセージにはテキストが含まれていません。", ephemeral=True)
        return

    await interaction.response.defer()

    status, payload = run_with_timeout(
        _analyze_text_worker, (content, True), 10)

    if status == "timeout":
        await interaction.followup.send(TIMEOUT_MSG)
        return

    if status == "ok":
        await interaction.followup.send(payload)
        return

    if status == "error":
        await interaction.followup.send(f"Error: {payload}")

if __name__ == "__main__":
    keep_alive()
    client.run(os.environ["TOKEN"])
