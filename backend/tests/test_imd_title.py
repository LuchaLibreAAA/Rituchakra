from app.providers.imd import humanize_cap_title, severity_from_title


def test_humanize_stacked_heavy_phrase():
    out = humanize_cap_title("Heavy to very heavy with extremely heavy rainfall", place="Nadia")
    assert out == "Extremely heavy rainfall warning — Nadia"
    assert "to very heavy with" not in out.lower()
    assert severity_from_title(out) == "extreme"


def test_humanize_plain_heavy():
    out = humanize_cap_title("Heavy rainfall warning for Gangetic West Bengal", place="Kolkata")
    assert out.startswith("Heavy rainfall warning")
    assert "Kolkata" in out
