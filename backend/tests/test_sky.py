from app.ml.sky import compass, flow_compass, flow_deg, rose_bins, sky_label


def test_sky_known_and_fallback():
    assert sky_label(0) == ("Clear sky", "clear")
    assert sky_label(61)[1] == "rain"
    assert sky_label(95)[1] == "storm"
    assert sky_label(None)[1] == "cloud"
    assert sky_label(97)[1] == "storm"


def test_compass_and_flow():
    assert compass(0) == "N"
    assert compass(180) == "S"
    assert compass(90) == "E"
    assert compass(270) == "W"
    assert compass(359) == "N"
    assert flow_deg(210) == 30
    assert flow_compass(210) == "NNE"


def test_rose_bins_counts():
    dirs = [0, 10, 180, 185, 90]
    speeds = [8, 10, 12, 14, 6]
    bins = rose_bins(dirs, speeds)
    by = {b["dir"]: b for b in bins}
    assert by["N"]["count"] == 2
    assert by["S"]["count"] == 2
    assert by["E"]["count"] == 1
    assert by["N"]["avg_speed"] == 9.0
