#!/usr/bin/env python3
"""
fuzzer.py -- Android Intent fuzzer to discover hidden components
Sends Intents with various action strings and fuzzes parameters
to find unexpected activities, services, and receivers.
Usage: python3 fuzzer.py --package com.example.app
"""
import subprocess, argparse, sys, itertools

INTENT_ACTIONS = [
    "android.intent.action.MAIN",
    "android.intent.action.VIEW", "android.intent.action.EDIT",
    "android.intent.action.SEND", "android.intent.action.SENDTO",
    "android.intent.action.SEARCH", "android.intent.action.DIAL",
    "android.intent.action.CALL", "android.intent.action.PICK",
    "android.intent.action.GET_CONTENT",
]

CUSTOM_ACTIONS = [
    "{pkg}.action.MAIN", "{pkg}.action.SETTINGS", "{pkg}.action.DEBUG",
    "{pkg}.action.HOME", "{pkg}.action.ABOUT", "{pkg}.action.TEST",
    "{pkg}.action.ADMIN", "{pkg}.action.BACKDOOR", "{pkg}.action.UNLOCK",
    "com.internal.{basename}.HIDDEN", "internal.debug.{basename}",
]

def adb(cmd):
    r = subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr

def start_activity(pkg, action):
    """Try to start activity with action, catch errors"""
    ok, out = adb(f"am start -a {action} -n {pkg}/.dummy 2>&1 || true")
    # If we see "Error: Unknown class" that's different than "No match found"
    # It means the component exists but we don't have the exact class
    if "No such option" not in out and "Invalid" not in out:
        return True
    return False

def send_broadcast(pkg, action):
    """Send broadcast with action"""
    ok, out = adb(f"am broadcast -a {action} --user all 2>&1 || true")
    # Activity might catch it without error
    return "broadcasts received" not in out or len(out) < 100

def fuzz_intents(pkg, actions):
    print(f"\n🎲 Fuzzing {pkg} with {len(actions)} actions")
    print("─" * 60)
    
    discovered = []
    for i, action in enumerate(actions):
        if (i + 1) % 10 == 0:
            print(f"  ... {i+1}/{len(actions)} tested", flush=True)
        
        # Try as activity
        if start_activity(pkg, action):
            print(f"  [Activity] {action}")
            discovered.append(("activity", action))
        
        # Try as broadcast
        if send_broadcast(pkg, action):
            print(f"  [Broadcast] {action}")
            discovered.append(("broadcast", action))
    
    return discovered

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--wordlist", help="Custom action wordlist")
    parser.add_argument("--custom-only", action="store_true")
    parser.add_argument("--fuzzy", action="store_true", help="Add random parameter fuzzing")
    args = parser.parse_args()

    basename = args.package.split('.')[-1]
    actions = []

    if not args.custom_only:
        actions.extend(INTENT_ACTIONS)
    
    actions.extend([a.format(pkg=args.package, basename=basename) for a in CUSTOM_ACTIONS])

    if args.wordlist:
        with open(args.wordlist) as f:
            actions.extend(f.read().splitlines())

    # Remove dupes
    actions = list(set(actions))

    discovered = fuzz_intents(args.package, actions)
    
    print(f"\n{'─'*60}")
    print(f"Found {len(discovered)} potential hidden components")
    for component_type, action in discovered:
        print(f"  {component_type}: {action}")

if __name__ == "__main__":
    main()
