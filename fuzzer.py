#!/usr/bin/env python3
"""
fuzzer.py -- Android Intent fuzzer
Generates random Intent payloads and sends them to the target app.
Usage: python3 fuzzer.py --app com.example.app --count 100 --silent
"""
import subprocess, argparse, random, string, json

def adb(cmd):
    return subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True, text=True).stdout.strip()

class IntentFuzzer:
    def __init__(self, app_package, count=100):
        self.app = app_package
        self.count = count
        self.crashes = []
        self.errors = []

    def random_string(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def random_int(self):
        return random.randint(-2147483648, 2147483647)

    def random_bool(self):
        return random.choice(["true", "false"])

    def generate_intent(self):
        """Generate a random Intent"""
        package, activity = self.app, ".MainActivity"
        action = f"com.example.ACTION_{self.random_string(8)}"
        data_uri = f"content://{self.random_string(12)}/{self.random_string(8)}"
        extras = {}
        for _ in range(random.randint(1, 5)):
            key = self.random_string(10)
            val_type = random.choice(["string", "int", "bool"])
            if val_type == "string":
                extras[key] = self.random_string(20)
            elif val_type == "int":
                extras[key] = self.random_int()
            else:
                extras[key] = self.random_bool()
        return {"action": action, "data": data_uri, "package": package, "activity": activity, "extras": extras}

    def send_intent(self, intent, verbose=False):
        """Send Intent via am start"""
        cmd = f"am start -a {intent['action']} -d {intent['data']}"
        for k, v in intent['extras'].items():
            cmd += f" -e {k} {v}"
        cmd += f" {intent['package']}/{intent['activity']} 2>&1"
        result = adb(cmd)
        if "Error" in result or "crash" in result.lower():
            self.errors.append((intent, result))
            if verbose: print(f"❌ {result[:80]}")
            return False
        return True

    def run(self, verbose=False):
        print(f"\n💉 Fuzzing {self.app} with {self.count} random Intents...")
        for i in range(self.count):
            intent = self.generate_intent()
            ok = self.send_intent(intent, verbose)
            if (i + 1) % 20 == 0:
                print(f"  [{i+1}/{self.count}] — Errors: {len(self.errors)}")
        print(f"\n✅ Fuzz complete. Found {len(self.errors)} errors.")
        if self.errors:
            with open("fuzz_crashes.json", "w") as f:
                json.dump([{"intent": e[0], "error": e[1]} for e in self.errors], f, indent=2)
            print("   Crashes saved to fuzz_crashes.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", required=True, help="Target package")
    parser.add_argument("--count", type=int, default=100, help="Number of fuzz tests")
    parser.add_argument("--verbose", action="store_true", help="Print all errors")
    args = parser.parse_args()

    fuzzer = IntentFuzzer(args.app, args.count)
    fuzzer.run(args.verbose)
