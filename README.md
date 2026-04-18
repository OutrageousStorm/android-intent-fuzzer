# 🎲 Android Intent Fuzzer

Discover hidden Android activities, broadcast receivers, and services via Intent fuzzing.

## What it does

- Enumerate all exported components
- Fuzz with random Intent data/extras
- Detect crashes and unhandled exceptions
- Log accessible services

## Usage

```bash
python3 fuzz.py --package com.example.app --count 100
python3 fuzz.py --broadcast  # fuzz all broadcast receivers
```
