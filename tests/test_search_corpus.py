"""CLI regression tests using a small synthetic corpus."""
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "neuro-marketing/scripts/search_corpus.py"
ARTICLE = {
    "pmcid": "PMC123",
    "doi": "10.0000/example",
    "source_url": "https://example.org/PMC123",
    "title": "Packaging and choice",
    "abstract": "Participants compared two labels.",
    "text": "Full results: café packaging was identified correctly.",
    "theme": "sensory-marketing",
    "page_count": 3,
    "license": "CC BY",
}


class SearchCorpusTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.corpus = Path(directory.name) / "corpus.jsonl.gz"
        with gzip.open(self.corpus, "wt", encoding="utf-8") as stream:
            for article in (ARTICLE, dict(ARTICLE, pmcid="PMC1234", title="Other paper")):
                stream.write(json.dumps(article) + "\n")

    def search(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--corpus", str(self.corpus)],
            cwd=self.corpus.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_legacy_json_search(self):
        result = self.search("packaging", "--theme", "sensory-marketing", "--top", "1", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        (record,) = json.loads(result.stdout)
        self.assertEqual(record["pmcid"], ARTICLE["pmcid"])
        self.assertIn("search_score", record)
        self.assertIn("evidence_snippet", record)
        self.assertNotIn("text", record)

    def test_exact_lookup_json_full_text(self):
        result = self.search("--pmcid", "pmc123", "--json", "--full-text")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [ARTICLE])

    def test_exact_lookup_plain_text_defaults_to_abstract(self):
        result = self.search("--pmcid", "PMC123")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(ARTICLE["abstract"], result.stdout)
        self.assertNotIn(ARTICLE["text"], result.stdout)

    def test_lookup_json_omits_full_text_by_default(self):
        result = self.search("--pmcid", "PMC123", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        (record,) = json.loads(result.stdout)
        self.assertNotIn("text", record)

    def test_full_text_plain_output(self):
        for args in (("--pmcid", "PMC123"), ("packaging", "--top", "1")):
            with self.subTest(args=args):
                result = self.search(*args, "--full-text")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(ARTICLE["text"], result.stdout)

    def test_legacy_json_full_text(self):
        result = self.search("packaging", "--top", "1", "--full-text", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        (record,) = json.loads(result.stdout)
        self.assertEqual(record["text"], ARTICLE["text"])
        self.assertIn("search_score", record)

    def test_unknown_pmcid(self):
        result = self.search("--pmcid", "PMC999")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Article not found", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_invalid_arguments(self):
        for args in ((), ("the and",), ("packaging", "--top", "-1"),
                     ("packaging", "--pmcid", "PMC123"), ("--pmcid", "123"),
                     ("--pmcid", "PMC123", "--theme", "pricing-value")):
            with self.subTest(args=args):
                result = self.search(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
