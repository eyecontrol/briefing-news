"""Regole per scegliere la sezione di una notizia e per scartare sport e spettacolo."""

import re
import unicodedata

SECTIONS = {
    "pol": "Politica",
    "war": "Guerre",
    "cat": "Catastrofi",
    "eco": "Economia e finanza",
    "sci": "Scienza",
    "med": "Medicina",
    "tec": "Tecnologia",
}


def _rx(words):
    return re.compile(r"\b(?:" + "|".join(words) + r")", re.IGNORECASE)


# Parole che fanno scartare la notizia (sport, spettacolo, gossip, stile di vita).
EXCLUDE_WORDS = _rx([
    r"calci(o|omercato)\b", r"serie a\b", r"champions league", r"europa league", r"premier league",
    r"formula ?1\b", r"motogp", r"tennis", r"sinner\b", r"olimpiad", r"olympic", r"mondiali di calcio",
    r"world cup", r"nba\b", r"nfl\b", r"football\b", r"soccer", r"rugby", r"cricket", r"golf\b",
    r"ciclismo", r"giro d'italia", r"tour de france", r"allenatore", r"gol\b", r"derby\b",
    r"juventus", r"napoli calcio", r"roma calcio", r"lazio calcio",
    r"oscar\b", r"oscars", r"golden globe", r"grammy", r"sanremo", r"x factor", r"grande fratello",
    r"festival di venezia", r"box office", r"red carpet", r"celebrit", r"gossip", r"vip\b",
    r"oroscopo", r"horoscope", r"ricett", r"recipe", r"moda\b", r"fashion", r"reality show",
    r"serie tv", r"netflix series", r"concerto\b", r"cantante", r"singer",
    r"attore\b", r"attrice", r"actor\b", r"actress", r"royal family", r"principe harry", r"prince harry",
    r"country diary", r"crossword", r"cruciverba", r"quiz\b", r"podcast", r"newsletter", r"firstft",
])

EXCLUDE_URL = re.compile(
    r"/(sport|sports|calcio|football|soccer|spettacoli|spettacolo|cultura|culture|people|gossip|moda|"
    r"fashion|lifestyle|lifeandstyle|life-and-style|food|cucina|viaggi|travel|motori|tv-and-radio|film|"
    r"music|musica|stage|books|libri|games|oroscopo|style|arts|entertainment|television)(/|$|-)",
    re.IGNORECASE,
)

# Parole che spostano una notizia in una sezione precisa.
WAR = _rx([
    r"guerr", r"war\b", r"wars\b", r"warfare", r"bombard", r"bomb", r"missil", r"drone", r"raid\b",
    r"airstrike", r"air strike", r"strikes? on", r"attacc", r"offensiv", r"esercit", r"army", r"troop",
    r"truppe", r"militar", r"military", r"soldat", r"soldier", r"cessate il fuoco", r"ceasefire",
    r"tregua", r"truce", r"invasion", r"fronte\b", r"nato\b", r"hamas",
    r"hezbollah", r"houthi", r"gaza", r"ucrain", r"ukrain", r"kyiv", r"kiev", r"insurg", r"ribell",
    r"rebel", r"terror", r"ostagg", r"hostage", r"conflitt", r"conflict", r"armi\b", r"weapons",
])

CAT = _rx([
    r"terremot", r"sism", r"earthquake", r"quake", r"tsunami", r"alluvion", r"inondaz", r"flood",
    r"uragan", r"hurricane", r"typhoon", r"tifone", r"ciclon", r"cyclone", r"tornado", r"incendi",
    r"wildfire", r"bushfire", r"eruzion", r"eruption", r"vulcan", r"volcan", r"frana", r"landslide",
    r"valanga", r"avalanche", r"siccit", r"drought", r"maltempo", r"allerta (rossa|meteo)", r"nubifrag",
    r"ondata di calore", r"heatwave", r"heat wave", r"carestia", r"famine", r"epidemi", r"pandemi",
    r"outbreak", r"disastr", r"disaster", r"naufrag", r"shipwreck", r"esplosion",
    r"explosion", r"incidente aereo", r"plane crash", r"deragliam", r"derail",
])

MED = _rx([
    r"vaccin", r"tumor", r"cancro", r"cancer", r"malatti", r"disease", r"terapi", r"therap", r"farmac",
    r"drug\b", r"drugs\b", r"ospedal", r"hospital", r"sanit", r"health", r"salute", r"medic", r"virus",
    r"infezion", r"infection", r"alzheimer", r"diabet", r"cardi", r"heart\b", r"clinical trial",
    r"studio clinico", r"oms\b", r"antibiotic",
])

TEC = _rx([
    r"intelligenza artificiale", r"artificial intelligence", r"\bai\b", r"\bia\b", r"chatbot", r"openai",
    r"chip", r"semicondutt", r"semiconductor", r"software", r"cyber", r"hacker", r"smartphone", r"apple\b",
    r"google\b", r"microsoft", r"meta\b", r"nvidia", r"robot", r"quantum", r"quantistic", r"5g\b",
    r"internet", r"digital", r"algoritm", r"algorithm", r"data cent", r"satellit",
])

SCI = _rx([
    r"scienz", r"scien", r"ricercator", r"researcher", r"studio pubblicato", r"study\b", r"astronom",
    r"spazio\b", r"space\b", r"nasa\b", r"esa\b", r"pianet", r"planet", r"galass", r"galax", r"fisic",
    r"physic", r"chimic", r"chemi", r"biolog", r"genetic", r"dna\b", r"clima", r"climate", r"fossil",
    r"evolu", r"specie", r"species", r"oceano", r"ocean",
])

ECO = _rx([
    r"econom", r"pil\b", r"gdp\b", r"inflazion", r"inflation", r"bce\b", r"ecb\b", r"fed\b",
    r"federal reserve", r"tassi", r"interest rate", r"borsa", r"stock", r"mercati", r"markets",
    r"spread", r"bilancio", r"budget", r"manovra", r"tariff", r"dazi", r"commerci", r"trade\b",
    r"banc", r"bank", r"finanz", r"financ", r"debito", r"debt", r"lavoro", r"jobs\b", r"occupazion",
    r"unemploy", r"petrolio", r"oil price", r"energia", r"energy",
])

POL = _rx([
    r"govern", r"elezion", r"election", r"parlament", r"parliament", r"senat", r"camera\b", r"minist",
    r"president", r"premier", r"partit", r"party\b", r"voto\b", r"vote\b", r"referendum", r"legge",
    r"law\b", r"riform", r"reform", r"diplomat", r"summit", r"vertice", r"sanzion", r"sanction",
    r"ue\b", r"eu\b", r"onu\b", r"united nations", r"trump", r"meloni", r"mattarella", r"congress",
])

# Notizie che riguardano l'Italia.
ITALY = _rx([
    r"ital(ia|y|ian[oaie]?|iano|iana|iani|iane|ians?)\b", r"meloni", r"mattarella", r"palazzo chigi",
    r"quirinale", r"montecitorio", r"farnesina", r"tajani", r"salvini", r"schlein", r"conte\b",
    r"roma\b", r"milano", r"milan\b", r"napoli", r"naples", r"torino", r"turin", r"venezia", r"venice",
    r"firenze", r"florence", r"bologna", r"genova", r"palermo", r"bari\b", r"sicili", r"sardegn",
    r"sardinia", r"lombardia", r"piemonte", r"veneto", r"toscana", r"tuscany", r"emilia", r"campania",
    r"calabria", r"puglia", r"lazio\b", r"liguria", r"marche\b", r"abruzzo", r"umbria", r"friuli",
    r"trentino", r"alto adige", r"basilicata", r"molise", r"valle d'aosta",
])


def normalize(text):
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def is_excluded(title, summary, url):
    if EXCLUDE_URL.search(url or ""):
        return True
    return bool(EXCLUDE_WORDS.search(title or ""))


def pick_section(default, title, summary):
    """Sceglie la sezione. Guerre e catastrofi prevalgono sul feed generico;
    i feed tematici (scienza, medicina, ecc.) restano nella loro sezione."""
    text = f"{title} {summary}"
    head = title or ""
    if default in (None, "pol"):
        if WAR.search(head):
            return "war"
        if CAT.search(head):
            return "cat"
        if default == "pol":
            return "pol"
        # Feed di cronaca: tengo solo ciò che rientra in una sezione voluta.
        for key, rx in (("war", WAR), ("cat", CAT), ("med", MED), ("tec", TEC), ("sci", SCI),
                        ("eco", ECO), ("pol", POL)):
            if rx.search(text):
                return key
        return None
    if default in ("eco", "sci", "tec") and CAT.search(head):
        return "cat"
    return default


def is_italy(feed_italy, title, summary):
    return feed_italy or bool(ITALY.search(f"{title} {summary}"))
