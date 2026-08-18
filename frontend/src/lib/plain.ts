import type { Locale } from "@/i18n/copy";
import type { DashboardSnapshot, RiskCard } from "@/types/dashboard";

export type Level = "ok" | "watch" | "alert";

export function levelOf(score?: number | null, high = 70, mid = 45): Level {
  const n = score ?? 0;
  if (n >= high) return "alert";
  if (n >= mid) return "watch";
  return "ok";
}

const LEVEL_WORD: Record<Locale, Record<Level, string>> = {
  en: { ok: "Low", watch: "Medium", alert: "High" },
  hi: { ok: "कम", watch: "मध्यम", alert: "उच्च" },
  bn: { ok: "কম", watch: "মাঝারি", alert: "উচ্চ" },
};

const RISK_NAME: Record<string, Record<Locale, string>> = {
  flood: { en: "Flood", hi: "बाढ़", bn: "বন্যা" },
  drought: { en: "Drought", hi: "सूखा", bn: "খরা" },
  heat: { en: "Heat", hi: "गर्मी", bn: "তাপ" },
  irrigation_need: { en: "Irrigation", hi: "सिंचाई", bn: "সেচ" },
  air_quality: { en: "Air", hi: "वायु", bn: "বায়ু" },
  livelihood: { en: "Livelihood", hi: "आजीविका", bn: "জীবিকা" },
  seismic: { en: "Seismic", hi: "भूकंप", bn: "ভূকম্প" },
  tsunami: { en: "Tsunami", hi: "सुनामी", bn: "সুনামি" },
};

const RISK_TIP: Record<string, Record<Locale, string>> = {
  flood: {
    en: "Low fields and drains may fill. Move seed, pumps and animals up.",
    hi: "निचले खेत और नाले भर सकते हैं। बीज, पंप, पशु ऊँचाई पर रखें।",
    bn: "নিচু জমি ও নালা ভরে যেতে পারে। বীজ, পাম্প, পশু উঁচুতে রাখুন।",
  },
  drought: {
    en: "Rain is short of normal. Save water; irrigate only the best plots.",
    hi: "बारिश सामान्य से कम है। पानी बचाएँ; सिर्फ अच्छे खेतों को दें।",
    bn: "বৃষ্টি স্বাভাবিকের চেয়ে কম। জল বাঁচান; ভালো জমিতেই সেচ দিন।",
  },
  heat: {
    en: "Avoid midday work. Drink water. Shade livestock.",
    hi: "दोपहर में काम न करें। पानी पिएँ। पशुओं को छाया दें।",
    bn: "দুপুরে কাজ এড়ান। জল খান। পশুকে ছায়া দিন।",
  },
  irrigation_need: {
    en: "Soil is thirsty and little rain is listed. A light watering may help.",
    hi: "मिट्टी सूखी है और बारिश कम दिख रही है। हल्की सिंचाई सोचें।",
    bn: "মাটি শুকনো, বৃষ্টি কম। হালকা সেচ ভাবা যায়।",
  },
  air_quality: {
    en: "Outdoor air is unhealthy. Keep children and anyone with asthma inside when you can.",
    hi: "बाहर की हवा खराब है। बच्चों और दमा वालों को जितना हो अंदर रखें।",
    bn: "বাইরের বাতাস খারাপ। শিশু ও হাঁপানিতে যারা আছেন, ভিতরে রাখুন।",
  },
  livelihood: {
    en: "Heat, flood or bad air may stop field work on some days.",
    hi: "गर्मी, बाढ़ या खराब हवा कुछ दिन खेत का काम रोक सकती है।",
    bn: "গরম, বন্যা বা খারাপ বাতাস কিছুদিন জমির কাজ আটকাতে পারে।",
  },
  seismic: {
    en: "A recent quake is on the official list. This is a notice, not a prediction.",
    hi: "सूची में हाल का भूकंप है। यह सूचना है, भविष्यवाणी नहीं।",
    bn: "তালিকায় সাম্প্রতিক ভূমিকম্প আছে। এটা নোটিশ, ভবিষ্যদ্বাণী নয়।",
  },
  tsunami: {
    en: "A sea bulletin is active. Follow district and INCOIS instructions on the coast.",
    hi: "समुद्री बुलेटिन सक्रिय है। तट पर जिला / INCOIS निर्देश मानें।",
    bn: "সমুদ্র বুলেটিন সক্রিয়। উপকূলে জেলা / INCOIS নির্দেশ মানুন।",
  },
};

export function levelWord(locale: Locale, level: Level) {
  return LEVEL_WORD[locale][level];
}

export function riskTitle(id: string, locale: Locale, fallback: string) {
  return RISK_NAME[id]?.[locale] || fallback;
}

export function riskTip(id: string, locale: Locale) {
  return RISK_TIP[id]?.[locale] || "";
}

export function todayStory(dash: DashboardSnapshot, locale: Locale): string {
  const act = dash.prescriptive.actions[0];
  const sky = dash.live?.sky?.label || dash.descriptive.current.sky_label || "";
  const rain = dash.predictive.precip_next_3d_mm;
  if (locale === "hi") {
    if (act?.id === "hold_irrigation") return `आकाश ${sky || "साफ़"}. अगले 3 दिन लगभग ${rain} मिमी बारिश — आज सिंचाई रोकें।`;
    if (act?.id === "apply_irrigation") return `बारिश कम दिख रही है (${rain} मिमी / 3 दिन). हल्की सिंचाई सोची जा सकती है।`;
    if (act?.action) return act.action;
    return `${sky || "मौसम"} · अगले 3 दिन ${rain} मिमी बारिश।`;
  }
  if (locale === "bn") {
    if (act?.id === "hold_irrigation") return `আকাশ ${sky || "পরিষ্কার"}. আগামী ৩ দিনে প্রায় ${rain} মিমি বৃষ্টি — আজ সেচ না দিলেই ভালো।`;
    if (act?.id === "apply_irrigation") return `বৃষ্টি কম (${rain} মিমি / ৩ দিন). হালকা সেচ ভাবা যায়।`;
    if (act?.action) return act.action;
    return `${sky || "আবহাওয়া"} · আগামী ৩ দিন ${rain} মিমি বৃষ্টি।`;
  }
  if (act?.id === "hold_irrigation") return `${sky || "The sky"} · about ${rain} mm rain in 3 days — skip irrigation today.`;
  if (act?.id === "apply_irrigation") return `Little rain listed (${rain} mm / 3 days). A light watering may help.`;
  if (act?.action) return act.action;
  return `${sky || "Weather"} · ${rain} mm rain expected in the next 3 days.`;
}

export function worstWatch(risks: RiskCard[]): RiskCard | undefined {
  return [...risks].sort((a, b) => b.score_pct - a.score_pct)[0];
}
