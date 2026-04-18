# 🎲 Android Intent Fuzzer

Node.js tool to fuzz Android Intents — discover hidden activities and crash vulnerabilities.

## Install
```bash
npm install
chmod +x fuzz.js
```

## Usage
```bash
node fuzz.js com.example.app
node fuzz.js com.example.app --actions 100 --depth 3
```

## What it does
- Discovers exposed activities in the APK's manifest
- Generates random Intent combos with:
  - Common actions (VIEW, SEND, EDIT, etc.)
  - Optional categories
  - Optional data URIs
- Tests each Intent; logs crashes

## Output
```
🎲 Intent Fuzzer — com.example.app
Actions: 20, Depth: 2

Found 5 activities

[1/20] ACTION_VIEW ✓
[2/20] ACTION_SEND ·
...
✅ Tested: 20 | Found: 3 | Crashed: 1
```

Great for security research and app hardening.
