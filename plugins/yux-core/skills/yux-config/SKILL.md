---
name: yux-config
description: Manage yux-core configuration settings. Triggers: "config", "settings", "change language", "set language", "配置", "设置", "更改语言", "设置语言".
allowed-tools: Read, Write, Glob, AskUserQuestion
---

# yux-config Skill

Manage configuration settings for yux-claude-hub plugins.

## Triggers

This skill activates when user mentions:
- "config", "settings", "preferences"
- "change language", "set language", "switch language"
- "配置", "设置", "更改语言", "设置语言"
- "設定", "言語変更"
- "설정", "언어 변경"

## Workflow

### Step 1: Read Current Configuration

Read `.claude/yux-config.json`:
- If exists, parse current settings
- If not exists, inform user and suggest `/yux-init`

### Step 2: Determine User Intent

Parse user request to determine what they want to change:

**Language changes**:
- "set language to Chinese" → `"zh"`
- "change to English" → `"en"`
- "日本語に変更" → `"ja"`
- "한국어로 변경" → `"ko"`
- "设置为中文" → `"zh"`

**Preference changes**:
- "enable emoji" → `preferences.emoji: true`
- "disable verbose" → `preferences.verbose: false`

**View settings**:
- "show config", "view settings" → display current config

### Step 3: Update Configuration

If user wants to change settings:

1. Read current config
2. Update specified field(s)
3. Write updated config back to file
4. Preserve other fields unchanged

### Step 4: Confirmation

Output confirmation in the configured language.

## Configuration

Before generating output, read `.claude/yux-config.json`:
- If `language` is set, output in that language
- If file doesn't exist, detect from user input or default to English

## Output Examples

> Output language follows `.claude/yux-config.json` setting

### View Configuration

```
=== Current Configuration ===

Language: Chinese (zh)
Emoji: disabled
Verbose: disabled

File: .claude/yux-config.json
```

### Update Configuration

```
=== Configuration Updated ===

Changed: language
From: en
To: zh

All yux plugins will now output in Chinese.
```

### Configuration Not Found

```
=== Configuration Not Found ===

No configuration file found at .claude/yux-config.json

Run /yux-init to initialize configuration.
```

## Supported Languages

| Code | Language |
|------|----------|
| `en` | English |
| `zh` | 中文 (Chinese) |
| `ja` | 日本語 (Japanese) |
| `ko` | 한국어 (Korean) |

## Notes

- Changes take effect immediately for all yux plugins
- Invalid language codes will be rejected
- Config file must be valid JSON
