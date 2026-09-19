# =====================================================
# CAMPUSMIND AI - ELEVENLABS DIAGNOSTIC & VERIFICATION TEST
# =====================================================

import os
import sys
import requests
from dotenv import load_dotenv

# Load env variables from backend .env
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))
load_dotenv()

from config.config import Config

def test_elevenlabs():
    print("=" * 60)
    print("  CAMPUSMIND AI — ELEVENLABS TTS DIAGNOSTIC TOOL")
    print("=" * 60)

    api_key = (Config.ELEVENLABS_API_KEY or "").strip()
    voice_id = Config.ELEVENLABS_VOICE_ID or "Xb7hH8MSUJpSbSDYk0k2"
    model_id = Config.ELEVENLABS_MODEL_ID or "eleven_flash_v2_5"

    print(f"\n[1] Configuration Check:")
    print(f"    - Voice ID   : {voice_id} (Alice - Educator)")

    print(f"    - Model ID   : {model_id}")
    print(f"    - API Key    : {'*' * (len(api_key)-4) + api_key[-4:] if len(api_key) > 4 else ('[MISSING]' if not api_key else 'SET')}")

    if not api_key or api_key == "your_elevenlabs_api_key_here":
        print("\n[!] ELEVENLABS_API_KEY is not set.")
        print("    Follow these steps to set it up:")
        print("    1. Sign up at https://elevenlabs.io (free tier gives 10,000 chars/month)")
        print("    2. Go to Profile icon -> API Keys")
        print("    3. Click 'Create Key', name it 'CampusMind', enable TTS permissions")
        print("    4. Copy your key and add it to bakend/.env as:")
        print("       ELEVENLABS_API_KEY=your_copied_key")
        print("=" * 60)
        return False

    print("\n[2] Verifying API Key with ElevenLabs User Endpoint...")
    user_url = "https://api.elevenlabs.io/v1/user"
    headers = {"xi-api-key": api_key}

    try:
        res = requests.get(user_url, headers=headers, timeout=10)
        if res.status_code == 200:
            user_data = res.json()
            sub = user_data.get("subscription", {})
            char_count = sub.get("character_count", 0)
            char_limit = sub.get("character_limit", 0)
            remaining = max(0, char_limit - char_count)
            tier = sub.get("tier", "unknown")
            print(f"    [OK] API Key is valid!")
            print(f"    - Tier            : {tier}")
            print(f"    - Chars Used      : {char_count:,} / {char_limit:,}")
            print(f"    - Remaining Chars : {remaining:,}")
        elif "missing_permissions" in res.text or "user_read" in res.text:
            print(f"    [NOTE] Key is valid, but 'user_read' permission was not enabled. Continuing to TTS test...")
        else:
            print(f"    [FAIL] Authentication error (HTTP {res.status_code}): {res.text}")
            return False

    except Exception as e:
        print(f"    [ERROR] Network error contacting ElevenLabs: {e}")
        return False

    print("\n[3] Testing Text-to-Speech with Real-time Lip-sync Timestamps...")
    test_phrase = "Hello! CampusMind AI voice assistant is online and ready."
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    payload = {
        "text": test_phrase,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    tts_headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        tts_res = requests.post(tts_url, json=payload, headers=tts_headers, timeout=20)
        if tts_res.status_code == 200:
            tts_data = tts_res.json()
            audio_b64 = tts_data.get("audio_base64", "")
            alignment = tts_data.get("alignment", {})
            chars = alignment.get("characters", [])
            print(f"    [OK] Speech synthesis successful!")
            print(f"    - Audio Base64 length : {len(audio_b64):,} chars")
            print(f"    - Alignment characters: {len(chars)} viseme timing markers")
            print(f"\n>>> Full ElevenLabs TTS pipeline is OPERATIONAL! <<<")
            print("=" * 60)
            return True
        else:
            print(f"    [FAIL] TTS generation failed (HTTP {tts_res.status_code}): {tts_res.text}")
            return False
    except Exception as e:
        print(f"    [ERROR] Exception during TTS generation: {e}")
        return False

if __name__ == "__main__":
    success = test_elevenlabs()
    sys.exit(0 if success else 1)
