# Initialize yux-core Configuration

Initialize project configuration for yux-claude-hub plugins.

**Usage**: `/yux-init`

## Input

Optional arguments: $ARGUMENTS

## Workflow

### Step 1: Check Existing Configuration

1. Check if `.claude/` directory exists
2. Check if `.claude/yux-config.json` already exists

If config exists:
- Show current configuration
- Ask user if they want to reset or keep existing settings

### Step 2: Language Selection

Ask user for preferred output language using AskUserQuestion:

**Question**: "Select your preferred output language for yux plugins"
**Options**:
- English (default)
- 中文 (Chinese)
- 日本語 (Japanese)
- 한국어 (Korean)

### Step 3: Create Configuration

1. Create `.claude/` directory if not exists
2. Write `.claude/yux-config.json`:

```json
{
  "language": "<selected-language-code>",
  "preferences": {
    "emoji": false,
    "verbose": false
  },
  "created_at": "<ISO-8601-timestamp>",
  "version": "1.0.0"
}
```

Language codes:
- English → `"en"`
- 中文 → `"zh"`
- 日本語 → `"ja"`
- 한국어 → `"ko"`

### Step 4: Confirmation

Output confirmation message (in selected language):

**English**:
```
Configuration initialized successfully!

File: .claude/yux-config.json
Language: English

All yux plugins will now use this configuration.
```

**Chinese**:
```
配置初始化成功！

文件: .claude/yux-config.json
语言: 中文

所有 yux 插件现在都将使用此配置。
```

**Japanese**:
```
設定の初期化が完了しました！

ファイル: .claude/yux-config.json
言語: 日本語

すべての yux プラグインがこの設定を使用します。
```

**Korean**:
```
구성 초기화 완료!

파일: .claude/yux-config.json
언어: 한국어

모든 yux 플러그인이 이 구성을 사용합니다.
```

## Error Handling

- If Write fails, inform user of the error
- Suggest manual creation if automated creation fails

## Notes

- This command only needs to run once per project
- Other yux plugins will automatically read this configuration
- Configuration can be modified later using the yux-config skill
