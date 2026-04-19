# 🎲 Android Intent Fuzzer

Discover hidden Android activities, services, and broadcast receivers by fuzzing Intent parameters and action strings.

## Usage

```bash
python3 fuzzer.py --package com.example.app
python3 fuzzer.py --package com.example.app --wordlist intents.txt
python3 fuzzer.py --package com.example.app --action-prefix com.custom --fuzzy
```

## What it finds

- Hidden activities not in manifest
- Custom broadcast receivers
- Unexposed intent filters
- Services callable via Intent
- Activities with permission-required filters
