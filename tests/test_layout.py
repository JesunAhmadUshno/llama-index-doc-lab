"""Portfolio standard checks: the lock holds, required files exist, no public grade."""
import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# SHA-256 of PREREGISTRATION.md as committed in 9534f68 (tag proposal-v1), before any code or result.
LOCKED_SHA256 = "91e9fea3e84b41bb5a9335c8e4ab03fc0e373ebe899975d0c00108eea24596cb"
GRADE = re.compile(r"of 10,000|/ ?10,?000|Grade:|\bgrade \d", re.IGNORECASE)


def test_preregistration_is_unchanged_since_the_lock():
    digest = hashlib.sha256((ROOT / "PREREGISTRATION.md").read_bytes()).hexdigest()
    assert digest == LOCKED_SHA256, \
        "PREREGISTRATION.md changed after its lock; record an amendment in DECISIONS.md instead"


def test_required_files_exist():
    need = ["README.md", "PREREGISTRATION.md", "AUDIT.md", "RESULTS.md", "DECISIONS.md", "CHANGELOG.md",
            "CITATION.cff", "SECURITY.md", "LICENSE", "data/questions.json", "results/raw_runs.json",
            "results/metrics.json", "results/verdicts.json"]
    missing = [p for p in need if not (ROOT / p).exists()]
    assert not missing, "missing: " + ", ".join(missing)


def test_no_public_grade():
    for path in sorted(ROOT.glob("*.md")):
        hit = GRADE.search(path.read_text())
        assert not hit, f"{path.name} carries a grade ({hit.group(0)!r}); grades are internal"
