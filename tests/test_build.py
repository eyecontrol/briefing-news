import json
import re
import tempfile
import unittest
from pathlib import Path

from briefing import build, classify

FIXTURES = Path(__file__).parent / "fixtures"
NOW = "2026-10-12T05:00:00+00:00"


class BuildFromFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = Path(tempfile.mkdtemp())
        rc = build.main(["--out", str(cls.out), "--fixtures", str(FIXTURES), "--now", NOW])
        assert rc == 0
        page = (cls.out / "index.html").read_text(encoding="utf-8")
        cls.page = page
        cls.data = json.loads(re.search(r"const stories = (\[.*?\]);\n", page).group(1))

    def titles(self):
        return [s["h"] for s in self.data]

    def test_sport_and_entertainment_excluded(self):
        joined = " ".join(self.titles())
        self.assertNotIn("Premier League", joined)
        self.assertNotIn("Oscar", joined)

    def test_old_and_unclassified_crime_dropped(self):
        joined = " ".join(self.titles())
        self.assertNotIn("Old story", joined)
        self.assertNotIn("gioielleria", joined)

    def test_same_story_from_two_outlets_is_merged_and_leads(self):
        quakes = [s for s in self.data if "earthquake" in s["h"].lower()]
        self.assertEqual(len(quakes), 1)
        self.assertEqual(quakes[0]["t"], "cat")
        self.assertEqual(len(quakes[0]["also"]), 1)
        self.assertIs(self.data[0], quakes[0])

    def test_sections_and_italy_flag(self):
        by_title = {s["h"]: s for s in self.data}
        self.assertEqual(by_title["Ceasefire talks resume in Cairo after overnight strikes on Gaza"]["t"], "war")
        meloni = by_title["Italy's Meloni meets EU leaders on migration pact"]
        self.assertEqual(meloni["t"], "pol")
        self.assertTrue(meloni["it"])
        allerta = by_title["Allerta rossa per maltempo in Liguria e Toscana"]
        self.assertEqual(allerta["t"], "cat")
        self.assertTrue(allerta["it"])
        self.assertEqual(by_title["Ocean heat uptake mapped over six decades"]["t"], "sci")

    def test_page_has_no_placeholders_left(self):
        self.assertNotRegex(self.page, r"__[A-Z]+__")
        self.assertIn("Lunedì 12 ottobre 2026", self.page)
        self.assertIn("Anno I · N. 1", self.page)


class Rules(unittest.TestCase):
    def test_same_event_with_different_wording_is_merged(self):
        items = [
            {"title": "One killed, 11 injured in second Houthi strike on Riyadh airport in two days"},
            {"title": "Houthis attack Riyadh airport"},
            {"title": "Pope Leo will have surgery to remove growth on lung"},
        ]
        groups = build.cluster(items)
        self.assertEqual([len(g["items"]) for g in groups], [2, 1])

    def test_columns_and_newsletters_excluded(self):
        self.assertTrue(classify.is_excluded("Country diary: Fungi season is here", "", "https://x/science/1"))

    def test_city_names_do_not_trigger_sport_filter(self):
        self.assertFalse(classify.is_excluded("Milan prosecutors open inquiry into bank", "", "https://x/world/1"))

    def test_url_section_excludes(self):
        self.assertTrue(classify.is_excluded("Anything", "", "https://www.corriere.it/spettacoli/1"))


if __name__ == "__main__":
    unittest.main()
