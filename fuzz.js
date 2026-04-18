#!/usr/bin/env node
/**
 * android-intent-fuzzer.js
 * Fuzz Android Intents to discover hidden/vulnerable activities
 * Usage: node fuzz.js <package> --actions 20 --depth 3
 */

const { exec } = require("child_process");
const fs = require("fs");

function adb(cmd) {
    return new Promise((resolve) => {
        exec(`adb shell ${cmd}`, (err, stdout) => {
            resolve(stdout.trim());
        });
    });
}

const COMMON_ACTIONS = [
    "android.intent.action.MAIN",
    "android.intent.action.VIEW",
    "android.intent.action.EDIT",
    "android.intent.action.SEND",
    "android.intent.action.SENDTO",
    "android.intent.action.SEARCH",
    "android.intent.action.CALL",
    "android.intent.action.DIAL",
    "android.intent.action.PICTURE_IN_PICTURE",
    "android.intent.action.MANAGE_NETWORK_USAGE",
    "com.example.ACTION_CUSTOM",
    "com.android.internal.intent.action.INTERNAL_SETTINGS",
];

const COMMON_CATEGORIES = [
    "android.intent.category.DEFAULT",
    "android.intent.category.LAUNCHER",
    "android.intent.category.BROWSABLE",
    "android.intent.category.TAB",
];

const COMMON_DATA = [
    "http://example.com",
    "https://example.com",
    "file:///sdcard/test",
    "content://contacts/people",
    "tel://1234567890",
    "sms://1234567890",
];

async function fuzzIntent(pkg, action, category, data) {
    let cmd = `am start -n ${pkg}/.DummyActivity`;
    cmd += ` -a ${action}`;
    if (category) cmd += ` -c ${category}`;
    if (data) cmd += ` -d "${data}"`;
    
    try {
        await adb(cmd);
        return true;
    } catch (e) {
        return false;
    }
}

async function discoverActivities(pkg) {
    const manifest = await adb(`dumpsys package ${pkg}`);
    const activities = [];
    for (const line of manifest.split("\n")) {
        if (line.includes("Activity") && line.includes(pkg)) {
            const m = line.match(/Activity (\S+)/);
            if (m) activities.push(m[1]);
        }
    }
    return activities;
}

async function main() {
    const pkg = process.argv[2];
    if (!pkg) {
        console.log("Usage: node fuzz.js <package> [--actions N] [--depth N]");
        process.exit(1);
    }

    const actionCount = parseInt(process.argv[4] || 20);
    const depth = parseInt(process.argv[6] || 2);

    console.log(`\n🎲 Intent Fuzzer — ${pkg}`);
    console.log(`Actions: ${actionCount}, Depth: ${depth}\n`);

    const activities = await discoverActivities(pkg);
    console.log(`Found ${activities.length} activities\n`);

    let found = 0;
    let crashed = 0;

    for (let i = 0; i < actionCount; i++) {
        const action = COMMON_ACTIONS[Math.floor(Math.random() * COMMON_ACTIONS.length)];
        const category = Math.random() > 0.5 ? COMMON_CATEGORIES[0] : null;
        const data = Math.random() > 0.5 ? COMMON_DATA[Math.floor(Math.random() * COMMON_DATA.length)] : null;

        process.stdout.write(`[${i+1}/${actionCount}] ${action.split(".").pop()}`);
        
        try {
            const ok = await fuzzIntent(pkg, action, category, data);
            if (ok) {
                console.log(" ✓");
                found++;
            } else {
                console.log(" ·");
            }
        } catch (e) {
            console.log(" ✗ CRASH");
            crashed++;
        }
    }

    console.log(`\n✅ Tested: ${actionCount} | Found: ${found} | Crashed: ${crashed}`);
}

main().catch(console.error);
