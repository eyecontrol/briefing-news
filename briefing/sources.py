"""Testate e feed RSS usati dal briefing.

Solo testate storiche e agenzie riconosciute. Ogni feed ha:
  - section: la sezione di partenza (None = feed generico, la sezione si
    deduce dalle parole chiave e, se non si trova, la notizia viene scartata)
  - italy: True se il feed copre solo fatti italiani
  - max_age_h: quante ore indietro guardare (le riviste scientifiche escono
    meno spesso dei quotidiani)
"""

# Testate: nome, anno di fondazione, gruppo nella gerenza, lingua.
OUTLETS = {
    "ANSA": (1945, "Italia", "IT"),
    "Corriere della Sera": (1876, "Italia", "IT"),
    "La Stampa": (1867, "Italia", "IT"),
    "Il Sole 24 Ore": (1865, "Italia", "IT"),
    "Il Messaggero": (1878, "Italia", "IT"),
    "la Repubblica": (1976, "Italia", "IT"),
    "The Guardian": (1821, "Internazionali", "EN"),
    "The New York Times": (1851, "Internazionali", "EN"),
    "The Washington Post": (1877, "Internazionali", "EN"),
    "BBC News": (1922, "Internazionali", "EN"),
    "Le Monde": (1944, "Internazionali", "EN"),
    "Der Spiegel International": (1947, "Internazionali", "EN"),
    "The Economist": (1843, "Economia e finanza", "EN"),
    "Financial Times": (1888, "Economia e finanza", "EN"),
    "The New England Journal of Medicine": (1812, "Medicina", "EN"),
    "The Lancet": (1823, "Medicina", "EN"),
    "The BMJ": (1840, "Medicina", "EN"),
    "Nature": (1869, "Scienza e tecnologia", "EN"),
    "Scientific American": (1845, "Scienza e tecnologia", "EN"),
    "MIT Technology Review": (1899, "Scienza e tecnologia", "EN"),
    "New Scientist": (1956, "Scienza e tecnologia", "EN"),
}


def feed(source, url, section=None, italy=False, max_age_h=30):
    return {"source": source, "url": url, "section": section, "italy": italy, "max_age_h": max_age_h}


FEEDS = [
    # Italia
    feed("ANSA", "https://www.ansa.it/sito/notizie/politica/politica_rss.xml", "pol", italy=True),
    feed("ANSA", "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml", "pol"),
    feed("ANSA", "https://www.ansa.it/sito/notizie/cronaca/cronaca_rss.xml", None, italy=True),
    feed("ANSA", "https://www.ansa.it/sito/notizie/economia/economia_rss.xml", "eco"),
    feed("ANSA", "https://www.ansa.it/sito/notizie/tecnologia/tecnologia_rss.xml", "tec"),
    feed("ANSA", "https://www.ansa.it/canale_scienza/notizie/scienza_rss.xml", "sci"),
    feed("ANSA", "https://www.ansa.it/canale_saluteebenessere/notizie/saluteebenessere_rss.xml", "med"),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/politica.xml", "pol", italy=True),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/esteri.xml", "pol"),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/cronache.xml", None, italy=True),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/economia.xml", "eco"),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/salute.xml", "med"),
    feed("Corriere della Sera", "https://xml2.corriereobjects.it/rss/tecnologia.xml", "tec"),
    feed("la Repubblica", "https://www.repubblica.it/rss/politica/rss2.0.xml", "pol", italy=True),
    feed("la Repubblica", "https://www.repubblica.it/rss/esteri/rss2.0.xml", "pol"),
    feed("la Repubblica", "https://www.repubblica.it/rss/economia/rss2.0.xml", "eco"),
    feed("la Repubblica", "https://www.repubblica.it/rss/scienze/rss2.0.xml", "sci"),
    feed("la Repubblica", "https://www.repubblica.it/rss/tecnologia/rss2.0.xml", "tec"),
    feed("La Stampa", "https://www.lastampa.it/rss/politica.xml", "pol", italy=True),
    feed("La Stampa", "https://www.lastampa.it/rss/esteri.xml", "pol"),
    feed("La Stampa", "https://www.lastampa.it/rss/economia.xml", "eco"),
    feed("La Stampa", "https://www.lastampa.it/rss/scienza.xml", "sci"),
    feed("Il Sole 24 Ore", "https://www.ilsole24ore.com/rss/italia.xml", "pol", italy=True),
    feed("Il Sole 24 Ore", "https://www.ilsole24ore.com/rss/mondo.xml", "pol"),
    feed("Il Sole 24 Ore", "https://www.ilsole24ore.com/rss/economia.xml", "eco"),
    feed("Il Sole 24 Ore", "https://www.ilsole24ore.com/rss/finanza.xml", "eco"),
    feed("Il Sole 24 Ore", "https://www.ilsole24ore.com/rss/tecnologia.xml", "tec"),
    feed("Il Messaggero", "https://www.ilmessaggero.it/rss/politica.xml", "pol", italy=True),
    feed("Il Messaggero", "https://www.ilmessaggero.it/rss/mondo.xml", "pol"),
    feed("Il Messaggero", "https://www.ilmessaggero.it/rss/economia.xml", "eco"),
    # Internazionali
    feed("BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml", "pol"),
    feed("BBC News", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "sci"),
    feed("BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml", "tec"),
    feed("BBC News", "https://feeds.bbci.co.uk/news/health/rss.xml", "med"),
    feed("BBC News", "https://feeds.bbci.co.uk/news/business/rss.xml", "eco"),
    feed("The Guardian", "https://www.theguardian.com/world/rss", "pol"),
    feed("The Guardian", "https://www.theguardian.com/science/rss", "sci"),
    feed("The Guardian", "https://www.theguardian.com/technology/rss", "tec"),
    feed("The Guardian", "https://www.theguardian.com/business/rss", "eco"),
    feed("The Guardian", "https://www.theguardian.com/society/health/rss", "med"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml", "pol"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", "pol"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml", "sci"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml", "med"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "tec"),
    feed("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml", "eco"),
    feed("The Washington Post", "https://feeds.washingtonpost.com/rss/world", "pol"),
    feed("The Washington Post", "https://feeds.washingtonpost.com/rss/politics", "pol"),
    feed("Le Monde", "https://www.lemonde.fr/en/rss/une.xml", "pol"),
    feed("Der Spiegel International", "https://www.spiegel.de/international/index.rss", "pol"),
    # Economia e finanza
    feed("The Economist", "https://www.economist.com/finance-and-economics/rss.xml", "eco", max_age_h=96),
    feed("The Economist", "https://www.economist.com/international/rss.xml", "pol", max_age_h=96),
    feed("The Economist", "https://www.economist.com/science-and-technology/rss.xml", "sci", max_age_h=96),
    feed("Financial Times", "https://www.ft.com/world?format=rss", "pol"),
    feed("Financial Times", "https://www.ft.com/global-economy?format=rss", "eco"),
    # Medicina
    feed("The New England Journal of Medicine", "https://www.nejm.org/action/showFeed?type=etoc&feed=rss&jc=nejm", "med", max_age_h=192),
    feed("The Lancet", "https://www.thelancet.com/rssfeed/lancet_online.xml", "med", max_age_h=192),
    feed("The BMJ", "https://www.bmj.com/rss/news.xml", "med", max_age_h=72),
    # Scienza e tecnologia
    feed("Nature", "https://www.nature.com/nature.rss", "sci", max_age_h=96),
    feed("Scientific American", "https://www.scientificamerican.com/platform/syndication/rss/", "sci", max_age_h=72),
    feed("MIT Technology Review", "https://www.technologyreview.com/feed/", "tec", max_age_h=72),
    feed("New Scientist", "https://www.newscientist.com/feed/home/", "sci", max_age_h=48),
]
