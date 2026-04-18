#!/usr/bin/env python3
"""
fuzz.py -- Android Intent fuzzer for discovering hidden components
Sends random Intents to activities/broadcast receivers/services
"""
import subprocess, random, string, argparse, json

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout

def get_exported_components(pkg):
    out = adb(f"dumpsys package {pkg}")
    activities = []
    for line in out.splitlines():
        if "Activity" in line:
            parts = line.strip().split()
            if parts and "/" in parts[0]:
                activities.append(parts[0].replace(".", "/"))
    return activities

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def fuzz_intent(activity, extra_count=3):
    cmd = f"am start -n {activity}"
    # Add random extras
    for i in range(extra_count):
        key = random_string(8)
        val = random_string(10)
        cmd += f" --es {key} {val}"
    result = adb(cmd)
    return "Error" in result or "ANR" in result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True)
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()

    print(f"Fuzzing {args.package}...")
    comps = get_exported_components(args.package)
    print(f"Found {len(comps)} exported components")

    crashes = 0
    for i in range(args.count):
        if comps:
            comp = random.choice(comps)
            if fuzz_intent(comp):
                crashes += 1
                print(f"  [CRASH] {comp}")

    print(f"\n{crashes}/{args.count} crashes found")

if __name__ == "__main__":
    main()
