#!/usr/bin/env python3
"""
fuzzer.py -- Fuzz Android Intents to discover hidden activities
Sends random intents with various actions, data URIs, and extras
to discover activities that might not be in the manifest.
Usage: python3 fuzzer.py [--target com.example.app] [--count 100]
"""
import subprocess, random, sys, argparse
from urllib.parse import urljoin

ACTIONS = [
    "android.intent.action.VIEW",
    "android.intent.action.EDIT",
    "android.intent.action.SEND",
    "android.intent.action.SEND_MULTIPLE",
    "android.intent.action.PICK",
    "android.intent.action.GET_CONTENT",
    "android.intent.action.OPEN_DOCUMENT",
    "android.intent.action.CALL",
    "android.intent.action.DIAL",
    "android.intent.action.SENDTO",
    "android.intent.action.SEARCH",
    "android.intent.action.WEB_SEARCH",
    "android.intent.action.CREATE_SHORTCUT",
    "com.example.ACTION_ADMIN",
    "com.example.ACTION_DEBUG",
    "com.example.DEEPLINK",
]

MIMETYPES = [
    "text/plain",
    "image/*",
    "image/jpeg",
    "application/json",
    "application/pdf",
    "application/x-www-form-urlencoded",
    "video/*",
    "audio/*",
]

URIS = [
    "http://example.com",
    "https://example.com/admin",
    "file:///sdcard/test.txt",
    "content://com.example.provider/data",
    "tel:1234567890",
    "mailto:test@example.com",
    "sms:1234567890",
    "geo:0,0?z=10",
]

CATEGORIES = [
    "android.intent.category.DEFAULT",
    "android.intent.category.BROWSABLE",
    "android.intent.category.LAUNCHER",
    "android.intent.category.ALTERNATIVE",
    "android.intent.category.SELECTED_ALTERNATIVE",
]

def adb_am(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.stdout + r.stderr

def fuzz_intent(target, action, data=None, mime=None, category=None):
    cmd = f"am start -a {action}"
    if data:
        cmd += f" -d {data}"
    if mime:
        cmd += f" -t {mime}"
    if category:
        cmd += f" -c {category}"
    if target:
        cmd += f" {target}"

    result = adb_am(cmd)
    
    # Check for successful launch vs error
    error = "Error" in result or "not found" in result.lower()
    return not error, cmd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", help="Target package (or empty for implicit)")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--action", help="Fuzz specific action")
    args = parser.parse_args()

    print(f"\n🎲 Android Intent Fuzzer")
    print(f"{'─'*50}")
    print(f"Target: {args.target or '(implicit)'}")
    print(f"Fuzzing {args.count} intents...\n")

    found = 0
    for i in range(args.count):
        action = args.action or random.choice(ACTIONS)
        data = random.choice(URIS) if random.random() > 0.5 else None
        mime = random.choice(MIMETYPES) if random.random() > 0.6 else None
        category = random.choice(CATEGORIES) if random.random() > 0.7 else None

        ok, cmd = fuzz_intent(args.target, action, data, mime, category)
        
        if ok:
            found += 1
            print(f"  ✓ [{i+1}] {action:<40} {data or ''}")
        elif i % 10 == 0:
            print(f"  ... {i}/{args.count}")

    print(f"\n{'─'*50}")
    print(f"✅ Fuzzing complete: {found} successful intents")
    print(f"💡 Check logcat for ANRs, crashes, or unexpected handlers")

if __name__ == "__main__":
    main()
