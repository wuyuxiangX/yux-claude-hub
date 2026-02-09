# yux-nano-banana

Generate images using OpenRouter API with Google Gemini models, directly from Claude Code.

## Features

- Text-to-image generation with natural language prompts
- Image editing (provide an existing image + instructions)
- Multiple model support (Flash for speed, Pro for quality)
- Multi-language support (English, Chinese, Japanese, Korean)
- Cross-platform compatibility (macOS / Linux)

## Installation

Add this plugin to your Claude Code configuration by including the plugin path in your settings.

## API Key Setup

You need an OpenRouter API key. Get one at [openrouter.ai/keys](https://openrouter.ai/keys).

### Option 1: Claude settings (Recommended)

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "OPENROUTER_API_KEY": "sk-or-..."
  }
}
```

### Option 2: Shell profile

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

### Option 3: Current session

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

> **Security**: Never store API keys in git-tracked files.

## Models

| Shorthand | Model ID | Description |
|-----------|----------|-------------|
| flash (default) | `google/gemini-2.5-flash-preview:image` | Fast and cost-effective |
| pro | `google/gemini-2.5-pro-preview:image` | Highest quality |

## Usage

The skill triggers automatically on keywords like "generate image", "draw", "nano banana", etc.

### Generate an image

```
generate image: a cute cat wearing a space helmet
```

### Use a specific model

```
draw with pro model: a photorealistic mountain landscape at sunset
```

### Edit an existing image

```
edit image ./photo.png: add a rainbow in the sky
```

## Output

Images are saved to the current directory as `nano-banana-YYYYMMDD-HHMMSS.png`.

## Requirements

- `curl` - HTTP requests
- `jq` - JSON parsing
- `base64` - Binary decoding

These tools are pre-installed on most macOS and Linux systems.
