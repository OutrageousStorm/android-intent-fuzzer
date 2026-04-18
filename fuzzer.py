#!/usr/bin/env python3
"""
fuzzer.py -- Fuzz Android Intent handlers with malformed data
Tests app robustness by sending crafted Intents via ADB.
Usage: python3 fuzzer.py --package com.example.app --iterations 100
"""
import subprocess, random, string, sys, argparse

def adb(cmd):
    subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True)

def fuzz_int():
    return random.choice([0, -1, 2**31-1, -2**31, random.randint(-1000000, 1000000)])

def fuzz_string(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def fuzz_uri():
    schemes = ['http://', 'https://', 'content://', 'file://', 'data://']
    return random.choice(schemes) + fuzz_string(30)

def fuzz_intent(pkg, action="android.intent.action.VIEW"):
    fuzzes = [
        # Normal
        f'am start -a {action} -n {pkg}/{pkg}.MainActivity',
        
        # Null intent
        f'am start -n {pkg}/',
        
        # Malformed URIs
        f'am start -a {action} -d "{fuzz_uri()}" {pkg}',
        
        # Large strings
        f'am start -e key "{fuzz_string(10000)}" {pkg}',
        
        # Negative numbers
        f'am start -e number {fuzz_int()} {pkg}',
        
        # Special characters
        f'am start -e data "$(>&2 echo pwned)" {pkg}',
        
        # Missing required args
        f'am start -a missing.action {pkg}',
        
        # Unicode
        f'am start -e unicode "🔒🎯💣" {pkg}',
    ]
    return random.choice(fuzzes)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, help="Target package")
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    print(f"\\n🎲 Android Intent Fuzzer")
    print(f"Target: {args.package}")
    print(f"Iterations: {args.iterations}")
    print("=" * 50)

    crashes = 0
    for i in range(args.iterations):
        intent = fuzz_intent(args.package)
        if args.verbose:
            print(f"[{i+1}] {intent[:80]}")
        adb(intent)
        
        # Check if app crashed
        result = subprocess.run(
            f"adb shell dumpsys activity | grep {args.package} | grep -i crash",
            shell=True, capture_output=True
        )
        if result.stdout:
            crashes += 1
            print(f"  💥 CRASH detected!")

    print("\\n" + "=" * 50)
    print(f"✅ Fuzzing complete: {crashes} crashes found in {args.iterations} iterations")

if __name__ == "__main__":
    main()
