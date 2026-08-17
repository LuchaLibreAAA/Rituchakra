"""Deterministic en/hi/bn narratives. The LLM does not generate Indic text."""

TEMPLATES: dict[str, dict[str, str]] = {
    "irrigation_hold_rain": {
        "en": "There is a possibility of {intensity} rain in the next {days} days ({rain_mm} mm, probability {prob}%). It is better not to irrigate today. This can save an estimated {liters_min}–{liters_max} liters of water.",
        "hi": "अगले {days} दिनों में {intensity} बारिश की संभावना है ({rain_mm} मिमी, संभावना {prob}%)। आज सिंचाई न करना बेहतर है। इससे अनुमानित {liters_min}–{liters_max} लीटर पानी बच सकता है।",
        "bn": "আগামী {days} দিনে {intensity} বৃষ্টির সম্ভাবনা রয়েছে ({rain_mm} মিমি, সম্ভাবনা {prob}%)। তাই আজ অতিরিক্ত সেচ না দেওয়াই ভালো। এতে আনুমানিক {liters_min}–{liters_max} লিটার জল সাশ্রয় হতে পারে।",
    },
    "irrigation_apply": {
        "en": "Little rain is expected in the next 3 days ({rain_mm} mm). Apply about {depth_mm} mm of irrigation today (~{liters} liters for a 400 m² plot).",
        "hi": "अगले 3 दिनों में कम बारिश अपेक्षित है ({rain_mm} मिमी)। आज लगभग {depth_mm} मिमी सिंचाई करें (400 वर्ग मीटर खेत पर ~{liters} लीटर)।",
        "bn": "আগামী ৩ দিনে বৃষ্টি কম ({rain_mm} মিমি)। আজ প্রায় {depth_mm} মিমি সেচ দিন (৪০০ বর্গমিটার জমিতে ~{liters} লিটার)।",
    },
    "flood_prep": {
        "en": "Flood risk is elevated (score {score}%). Move livestock, seed and pumps to higher ground, and clear local drains.",
        "hi": "बाढ़ का जोखिम बढ़ा हुआ है (स्कोर {score}%)। पशु, बीज और पंप ऊँचाई पर शिफ्ट करें और नालियाँ साफ़ रखें।",
        "bn": "বন্যার ঝুঁকি বেড়েছে (স্কোর {score}%)। গবাদিপশু, বীজ ও পাম্প উঁচু স্থানে সরান এবং নালা পরিষ্কার রাখুন।",
    },
    "drought_conserve": {
        "en": "Drought risk is elevated (score {score}%). Mulch, irrigate only at dawn or dusk, and skip non-critical plots.",
        "hi": "सूखे का जोखिम बढ़ा है (स्कोर {score}%)। मल्च करें, केवल सुबह/शाम सिंचाई करें, गैर-ज़रूरी खेत छोड़ दें।",
        "bn": "খরার ঝুঁকি বেড়েছে (স্কোর {score}%)। মালচ করুন, শুধু ভোর/সন্ধ্যায় সেচ দিন, অপ্রয়োজনীয় জমি বাদ দিন।",
    },
    "heat_protect": {
        "en": "Heat risk is elevated (score {score}%). Avoid midday field work and keep drinking water in the field.",
        "hi": "गर्मी का जोखिम बढ़ा है (स्कोर {score}%)। दोपहर में खेत का काम टालें और पीने का पानी साथ रखें।",
        "bn": "তাপদাহের ঝুঁকি বেড়েছে (স্কোর {score}%)। দুপুরে মাঠের কাজ এড়িয়ে চলুন এবং খাবার জল সঙ্গে রাখুন।",
    },
    "forecast_summary": {
        "en": "Next 3 days: {rain_mm} mm of rain (peak probability {prob}%), max temps {tmax}. Soil moisture is {soil}.",
        "hi": "अगले 3 दिन: {rain_mm} मिमी बारिश (शीर्ष संभावना {prob}%), अधिकतम तापमान {tmax}। मिट्टी की नमी {soil} है।",
        "bn": "আগামী ৩ দিন: {rain_mm} মিমি বৃষ্টি (সর্বোচ্চ সম্ভাবনা {prob}%), সর্বোচ্চ তাপমাত্রা {tmax}। মাটির আর্দ্রতা {soil}।",
    },
    "aqi_protect": {
        "en": "CPCB National AQI is {aqi} ({category}), driven by {pollutant}. Limit outdoor field work and use a mask in dusty conditions.",
        "hi": "CPCB राष्ट्रीय AQI {aqi} है ({category}), मुख्य प्रदूषक {pollutant}। बाहर खेत का काम सीमित करें और धूल में मास्क पहनें।",
        "bn": "CPCB জাতীয় AQI {aqi} ({category}), প্রধান দূষক {pollutant}। বাইরের মাঠের কাজ সীমিত করুন এবং ধুলোয় মাস্ক ব্যবহার করুন।",
    },
    "mandi_summary": {
        "en": "Today's mandi: {summary}.",
        "hi": "आज की मंडी: {summary}।",
        "bn": "আজকের মান্ডি: {summary}।",
    },
    "generic_grounded": {
        "en": "{body}",
        "hi": "{body}",
        "bn": "{body}",
    },
}

INTENSITY = {
    "heavy": {"en": "heavy", "hi": "भारी", "bn": "ভারী"},
    "moderate to heavy": {"en": "moderate to heavy", "hi": "मध्यम से भारी", "bn": "মাঝারি থেকে ভারী"},
    "light to moderate": {"en": "light to moderate", "hi": "हल्की से मध्यम", "bn": "হালকা থেকে মাঝারি"},
}


def render(template_id: str, locale: str, slots: dict) -> str:
    lang = locale if locale in {"en", "hi", "bn"} else "en"
    tpl = TEMPLATES.get(template_id, TEMPLATES["generic_grounded"]).get(lang) or TEMPLATES["generic_grounded"]["en"]
    data = dict(slots)
    intensity = data.get("intensity")
    if isinstance(intensity, str) and intensity in INTENSITY:
        data["intensity"] = INTENSITY[intensity][lang]
    try:
        return tpl.format(**data)
    except Exception:
        return tpl
