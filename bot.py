# -*- coding: utf-8 -*-
"""
Р‘РѕС‚-РІРёРґР°С‡Р° РїСЂРѕРјРїС‚С–РІ РґР»СЏ РєРѕРјР°РЅРґРё РѕРЅР»Р°Р№РЅ-С€РєРѕР»Рё.

РЇРє С†Рµ РїСЂР°С†СЋС”:
- Р›СЋРґРёРЅР° РїРёС€Рµ /start -> Р±Р°С‡РёС‚СЊ РјРµРЅСЋ РІС–РґРґС–Р»С–РІ (РєРЅРѕРїРєРё).
- РћР±РёСЂР°С” РІС–РґРґС–Р» -> Р±Р°С‡РёС‚СЊ СЃРїРёСЃРѕРє РїСЂРѕРјРїС‚С–РІ С†СЊРѕРіРѕ РІС–РґРґС–Р»Сѓ (РєРЅРѕРїРєРё).
- РћР±РёСЂР°С” РїСЂРѕРјРїС‚ -> Р±РѕС‚ РЅР°РґСЃРёР»Р°С” Р‘С–Р»СЊ, Р—Р°РІРґР°РЅРЅСЏ, РіРѕС‚РѕРІРёР№ С‚РµРєСЃС‚ РїСЂРѕРјРїС‚Сѓ
  (РѕРґРЅРёРј РїРѕРІС–РґРѕРјР»РµРЅРЅСЏРј, Р· РєРѕРґРѕРІРёРј Р±Р»РѕРєРѕРј вЂ” Telegram СЃР°Рј РїРѕРєР°Р¶Рµ РєРЅРѕРїРєСѓ
  "СЃРєРѕРїС–СЋРІР°С‚Рё" РЅР° РґРѕРІРіРѕРјСѓ С‚РµРєСЃС‚С–) С– РєРѕСЂРѕС‚РєСѓ С–РЅСЃС‚СЂСѓРєС†С–СЋ "СЏРє РєРѕСЂРёСЃС‚СѓРІР°С‚РёСЃСЊ".
- РЇРєС‰Рѕ Р»СЋРґРёРЅР° РїСЂРѕСЃС‚Рѕ РїРёС€Рµ С‚РµРєСЃС‚ (РЅРµ РєРЅРѕРїРєРѕСЋ) вЂ” Р±РѕС‚ С€СѓРєР°С” Р·Р±С–РіРё
  Р·Р° Р·Р°РіРѕР»РѕРІРєР°РјРё С– Р‘РѕР»РµРј СѓСЃС–С… РїСЂРѕРјРїС‚С–РІ С– РїСЂРѕРїРѕРЅСѓС” СЃС…РѕР¶С– РІР°СЂС–Р°РЅС‚Рё.

Р—Р°Р»РµР¶РЅРѕСЃС‚С–: Р»РёС€Рµ РјРѕРґСѓР»СЊ `requests` (СЃС‚Р°РЅРґР°СЂС‚РЅРёР№, С” РјР°Р№Р¶Рµ РІСЃСЋРґРё).
РќРµ РІРёРєРѕСЂРёСЃС‚РѕРІСѓС” aiogram/python-telegram-bot СЃРїРµС†С–Р°Р»СЊРЅРѕ вЂ” РјРµРЅС€Рµ С€Р°РЅСЃС–РІ
Р·Р»РѕРІРёС‚Рё РЅРµСЃСѓРјС–СЃРЅС–СЃС‚СЊ РІРµСЂСЃС–Р№ Р±С–Р±Р»С–РѕС‚РµРєРё РїСЂРё СЂРѕР·РіРѕСЂС‚Р°РЅРЅС–.

Р—РђРџРЈРЎРљ:
  1. pip install requests
  2. Р’СЃС‚Р°РЅРѕРІС–С‚СЊ Р·РјС–РЅРЅСѓ СЃРµСЂРµРґРѕРІРёС‰Р° BOT_TOKEN (РґРёРІ. С–РЅСЃС‚СЂСѓРєС†С–СЋ РІ README.md)
  3. python bot.py

Р‘РѕС‚ РїСЂР°С†СЋС” С‡РµСЂРµР· long polling вЂ” С†Рµ РѕР·РЅР°С‡Р°С”, С‰Рѕ РїСЂРѕС†РµСЃ РјР°С” Р±СѓС‚Рё
РїРѕСЃС‚С–Р№РЅРѕ Р·Р°РїСѓС‰РµРЅРёР№ (РґРёРІ. README.md РїСЂРѕ Р±РµР·РєРѕС€С‚РѕРІРЅРёР№ С…РѕСЃС‚РёРЅРі Railway/Render).
"""

import os
import time
import logging
from typing import Optional

import requests

from data import DEPARTMENTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("prompts-bot")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit(
        "РќРµ Р·Р°РґР°РЅРѕ BOT_TOKEN. Р’СЃС‚Р°РЅРѕРІС–С‚СЊ Р·РјС–РЅРЅСѓ СЃРµСЂРµРґРѕРІРёС‰Р° BOT_TOKEN "
        "(С‚РѕРєРµРЅ РѕС‚СЂРёРјР°С”С‚Рµ Сѓ @BotFather РІ Telegram) С– Р·Р°РїСѓСЃС‚С–С‚СЊ Р·РЅРѕРІСѓ."
    )

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
MAX_TG_MESSAGE = 4096  # Р»С–РјС–С‚ Telegram РЅР° РґРѕРІР¶РёРЅСѓ РѕРґРЅРѕРіРѕ РїРѕРІС–РґРѕРјР»РµРЅРЅСЏ


def api(method: str, **params):
    """РџСЂРѕСЃС‚РёР№ РІРёРєР»РёРє РјРµС‚РѕРґСѓ Telegram Bot API."""
    try:
        resp = requests.post(f"{API_URL}/{method}", json=params, timeout=30)
        data = resp.json()
        if not data.get("ok"):
            log.warning("API error on %s: %s", method, data)
        return data
    except requests.RequestException as e:
        log.warning("Network error on %s: %s", method, e)
        return {"ok": False}


def send_message(chat_id: int, text: str, reply_markup: Optional[dict] = None, parse_mode: str = "HTML"):
    """РќР°РґСЃРёР»Р°РЅРЅСЏ РїРѕРІС–РґРѕРјР»РµРЅРЅСЏ Р· Р°РІС‚РѕРјР°С‚РёС‡РЅРёРј РїРѕРґС–Р»РѕРј, СЏРєС‰Рѕ С‚РµРєСЃС‚ РґРѕРІС€РёР№ Р·Р° Р»С–РјС–С‚ Telegram."""
    if len(text) <= MAX_TG_MESSAGE:
        return api("sendMessage", chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    # Р С–Р¶РµРјРѕ РїРѕ Р°Р±Р·Р°С†Р°С…, С‰РѕР± РЅРµ СЂРѕР·С–СЂРІР°С‚Рё С‚РµРєСЃС‚ РїСЂРѕРјРїС‚Сѓ РїРѕСЃРµСЂРµРґРёРЅС– СЃР»РѕРІР°
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > MAX_TG_MESSAGE - 100:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current:
        chunks.append(current)
    result = None
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        result = api(
            "sendMessage",
            chat_id=chat_id,
            text=chunk,
            reply_markup=reply_markup if is_last else None,
            parse_mode=parse_mode,
        )
    return result


def answer_callback(callback_query_id: str, text: str = ""):
    api("answerCallbackQuery", callback_query_id=callback_query_id, text=text)


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- РљР»Р°РІС–Р°С‚СѓСЂРё ----------

def departments_keyboard() -> dict:
    rows = []
    for dept_id, dept in DEPARTMENTS.items():
        rows.append([{"text": dept["label"], "callback_data": f"dept:{dept_id}"}])
    return {"inline_keyboard": rows}


def prompts_keyboard(dept_id: str) -> dict:
    dept = DEPARTMENTS[dept_id]
    rows = []
    for p in dept["prompts"]:
        rows.append([{"text": p["title"], "callback_data": f"prompt:{dept_id}:{p['id']}"}])
    rows.append([{"text": "в¬…пёЏ РќР°Р·Р°Рґ РґРѕ РІС–РґРґС–Р»С–РІ", "callback_data": "back:depts"}])
    return {"inline_keyboard": rows}


def back_keyboard(dept_id: str) -> dict:
    return {"inline_keyboard": [[{"text": "в¬…пёЏ РќР°Р·Р°Рґ РґРѕ СЃРїРёСЃРєСѓ", "callback_data": f"dept:{dept_id}"}]]}


# ---------- РџРѕС€СѓРє ----------

def find_prompt(dept_id: str, prompt_id: str):
    dept = DEPARTMENTS.get(dept_id)
    if not dept:
        return None
    for p in dept["prompts"]:
        if p["id"] == prompt_id:
            return p
    return None


STOP_WORDS = {
    "С–", "Р№", "РІ", "Сѓ", "РЅРµ", "РЅР°", "Р·", "С–Р·", "РїРѕ", "РґР»СЏ", "СЏРє", "С‰Рѕ", "С†Рµ",
    "РґРѕ", "Р°Р»Рµ", "Р°", "СЏ", "РјРё", "РІРё", "РІС–РЅ", "РІРѕРЅР°", "РІРѕРЅРё", "РјРµРЅС–", "РјС–Р№", "РјРѕСЏ",
    "С…РѕС‡Сѓ", "РїРѕС‚СЂС–Р±РЅРѕ", "С‚СЂРµР±Р°", "С‰РѕР±", "СЏРєС‰Рѕ", "Р°Р±Рѕ", "С‚РµР¶", "РІР¶Рµ", "РґСѓР¶Рµ",
}


def _keywords(text: str):
    words = [w.strip(".,!?()В«В»\"'") for w in text.lower().split()]
    return [w for w in words if len(w) >= 3 and w not in STOP_WORDS]


def search_prompts(query: str, limit: int = 8):
    """РЁСѓРєР°С” Р·Р° Р·Р°РіРѕР»РѕРІРєРѕРј, Р‘РѕР»РµРј С– Р—Р°РІРґР°РЅРЅСЏРј Сѓ РІСЃС–С… РІС–РґРґС–Р»Р°С….

    Р РѕР·Р±РёРІР°С” Р·Р°РїРёС‚ РЅР° РѕРєСЂРµРјС– СЃР»РѕРІР° (Р° РЅРµ С€СѓРєР°С” С„СЂР°Р·Сѓ С†С–Р»РєРѕРј) С– РїРѕСЂС–РІРЅСЋС”
    Р·Р° РїРѕС‡Р°С‚РєРѕРј СЃР»РѕРІР° (РїРµСЂС€С– 5 Р»С–С‚РµСЂ) вЂ” С†Рµ РіСЂСѓР±РёР№, Р°Р»Рµ СЂРѕР±РѕС‡РёР№ Р°РЅР°Р»РѕРі
    СЃС‚РµРјС–РЅРіСѓ, С‰РѕР± В«Р·Р°РїРµСЂРµС‡РµРЅРЅСЏВ» Р·РЅР°С…РѕРґРёР»Рѕ В«Р·Р°РїРµСЂРµС‡РµРЅСЊВ» С‚РѕС‰Рѕ.
    РџРѕРІРµСЂС‚Р°С” СЃРїРёСЃРѕРє (dept_id, prompt), РІС–РґСЃРѕСЂС‚РѕРІР°РЅРёР№ Р·Р° РєС–Р»СЊРєС–СЃС‚СЋ Р·Р±С–РіС–РІ.
    """
    q_words = _keywords(query)
    if not q_words:
        return []
    stems = [w[:5] if len(w) > 5 else w for w in q_words]
    scored = []
    for dept_id, dept in DEPARTMENTS.items():
        for p in dept["prompts"]:
            haystack = f"{p['title']} {p['pain']} {p['task']}".lower()
            score = sum(1 for s in stems if s in haystack)
            if score > 0:
                scored.append((score, dept_id, p))
    scored.sort(key=lambda x: -x[0])
    return [(dept_id, p) for _, dept_id, p in scored[:limit]]


# ---------- Р¤РѕСЂРјР°С‚СѓРІР°РЅРЅСЏ РІС–РґРїРѕРІС–РґС– Р· РїСЂРѕРјРїС‚РѕРј ----------

def format_prompt_message(dept_id: str, p: dict) -> str:
    return (
        f"<b>{escape_html(p['title'])}</b>\n\n"
        f"рџ’Ў <b>Р‘С–Р»СЊ:</b> {escape_html(p['pain'])}\n\n"
        f"рџЋЇ <b>Р—Р°РІРґР°РЅРЅСЏ:</b> {escape_html(p['task'])}\n\n"
        f"<b>РџСЂРѕРјРїС‚ (СЃРєРѕРїС–СЋР№С‚Рµ РїРѕРІРЅС–СЃС‚СЋ):</b>\n"
        f"<pre>{escape_html(p['prompt'])}</pre>\n\n"
        f"рџ”§ <b>РЇРє РєРѕСЂРёСЃС‚СѓРІР°С‚РёСЃСЊ:</b> {escape_html(p['howto'])}"
    )


# ---------- РћР±СЂРѕР±РЅРёРєРё ----------

def handle_start(chat_id: int):
    text = (
        "рџ‘‹ РџСЂРёРІС–С‚! Р¦Рµ Р±РѕС‚-Р±С–Р±Р»С–РѕС‚РµРєР° РіРѕС‚РѕРІРёС… РЁР†-РїСЂРѕРјРїС‚С–РІ РґР»СЏ РєРѕРјР°РЅРґРё.\n\n"
        "РћР±РµСЂС–С‚СЊ РІС–РґРґС–Р» РєРЅРѕРїРєРѕСЋ РЅРёР¶С‡Рµ вЂ” Р°Р±Рѕ РїСЂРѕСЃС‚Рѕ РЅР°РїРёС€С–С‚СЊ СЃР»РѕРІР°РјРё РІР°С€Сѓ РїСЂРѕР±Р»РµРјСѓ "
        "(РЅР°РїСЂРёРєР»Р°Рґ В«Р·Р°РїРµСЂРµС‡РµРЅРЅСЏВ» Р°Р±Рѕ В«РЅРµРіР°С‚РёРІВ»), С– СЏ Р·РЅР°Р№РґСѓ РїРѕС‚СЂС–Р±РЅРёР№ РїСЂРѕРјРїС‚."
    )
    send_message(chat_id, text, reply_markup=departments_keyboard())


def handle_text(chat_id: int, text: str):
    if text.strip().startswith("/start"):
        handle_start(chat_id)
        return

    results = search_prompts(text)
    if not results:
        send_message(
            chat_id,
            "РќС–С‡РѕРіРѕ РЅРµ Р·РЅР°Р№С€РѕРІ Р·Р° С†РёРј СЃР»РѕРІРѕРј рџ¤” РЎРїСЂРѕР±СѓР№С‚Рµ С–РЅС€Рµ РєР»СЋС‡РѕРІРµ СЃР»РѕРІРѕ "
            "(РЅР°РїСЂРёРєР»Р°Рґ С‡Р°СЃС‚РёРЅСѓ РїСЂРѕР±Р»РµРјРё: В«РїРѕРІРµСЂРЅРµРЅРЅСЏВ», В«РІРёРіРѕСЂР°РЅРЅСЏВ», В«РґРѕРјР°С€РєР°В») "
            "Р°Р±Рѕ РѕР±РµСЂС–С‚СЊ РІС–РґРґС–Р» Р· РјРµРЅСЋ: /start",
        )
        return

    rows = [
        [{"text": f"{DEPARTMENTS[d]['label']} вЂ” {p['title']}", "callback_data": f"prompt:{d}:{p['id']}"}]
        for d, p in results
    ]
    send_message(
        chat_id,
        f"Р—РЅР°Р№С€РѕРІ {len(results)} РІС–РґРїРѕРІС–РґРЅРёС… РїСЂРѕРјРїС‚С–РІ:",
        reply_markup={"inline_keyboard": rows},
    )


def handle_callback(callback_query: dict):
    cq_id = callback_query["id"]
    chat_id = callback_query["message"]["chat"]["id"]
    message_id = callback_query["message"]["message_id"]
    data = callback_query.get("data", "")

    if data == "back:depts":
        answer_callback(cq_id)
        api("editMessageReplyMarkup", chat_id=chat_id, message_id=message_id, reply_markup=departments_keyboard())
        return

    if data.startswith("dept:"):
        dept_id = data.split(":", 1)[1]
        dept = DEPARTMENTS.get(dept_id)
        answer_callback(cq_id)
        if not dept:
            return
        api(
            "editMessageText",
            chat_id=chat_id,
            message_id=message_id,
            text=f"{dept['label']} вЂ” РѕР±РµСЂС–С‚СЊ РїСЂРѕРјРїС‚:",
            reply_markup=prompts_keyboard(dept_id),
        )
        return

    if data.startswith("prompt:"):
        _, dept_id, prompt_id = data.split(":", 2)
        p = find_prompt(dept_id, prompt_id)
        answer_callback(cq_id)
        if not p:
            send_message(chat_id, "РџСЂРѕРјРїС‚ РЅРµ Р·РЅР°Р№РґРµРЅРѕ, СЃРїСЂРѕР±СѓР№С‚Рµ /start С‰Рµ СЂР°Р·.")
            return
        send_message(chat_id, format_prompt_message(dept_id, p), reply_markup=back_keyboard(dept_id))
        return

    answer_callback(cq_id)


# ---------- Р“РѕР»РѕРІРЅРёР№ С†РёРєР» (long polling) ----------

def run():
    log.info("Р‘РѕС‚ Р·Р°РїСѓС‰РµРЅРѕ, С‡РµРєР°СЋ РїРѕРІС–РґРѕРјР»РµРЅСЊ...")
    offset = 0
    while True:
        try:
            resp = api("getUpdates", offset=offset, timeout=25)
        except Exception as e:
            log.warning("Polling error: %s", e)
            time.sleep(3)
            continue

        if not resp or not resp.get("ok"):
            time.sleep(3)
            continue

        for update in resp.get("result", []):
            offset = update["update_id"] + 1
            try:
                if "message" in update and "text" in update["message"]:
                    chat_id = update["message"]["chat"]["id"]
                    handle_text(chat_id, update["message"]["text"])
                elif "callback_query" in update:
                    handle_callback(update["callback_query"])
            except Exception as e:
                log.exception("РџРѕРјРёР»РєР° РѕР±СЂРѕР±РєРё Р°РїРґРµР№С‚Сѓ: %s", e)


if __name__ == "__main__":
    run()
