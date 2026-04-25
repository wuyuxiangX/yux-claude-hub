# yux-nano-banana

Universal image generation via OpenRouter API, directly from Claude Code. Use any OpenRouter image-generation model — Gemini, Flux, or any other `provider/model-id` — with per-run model selection and optional prompt optimization.

## Features

- Text-to-image generation with natural language prompts
- Image editing (provide an existing image + instructions)
- **Any OpenRouter image model** — pass a full `provider/model-id` or use the `flash` / `pro` shorthands
- **Per-run model selection** — the skill asks you to pick a model when you don't specify one (no silent default)
- **Prompt optimization** — short or abstract prompts can be enriched with visual detail before the API call
- Style presets (e.g., `infographic`)
- Multi-language support (English, Chinese, Japanese, Korean)
- Cross-platform compatibility (macOS / Linux)

## Installation

Add this plugin to your Claude Code configuration by including the plugin path in your settings.

## API Key Setup

You need an OpenRouter API key. Get one at [openrouter.ai/keys](https://openrouter.ai/keys).

The image-generation skills in this hub read the key from the dedicated `OPENROUTER_IMAGE_API_KEY` environment variable, so you can isolate image billing/quota from other OpenRouter usage.

### Option 1: Claude settings (Recommended)

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "OPENROUTER_IMAGE_API_KEY": "sk-or-..."
  }
}
```

### Option 2: Shell profile

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export OPENROUTER_IMAGE_API_KEY="sk-or-..."
```

### Option 3: Current session

```bash
export OPENROUTER_IMAGE_API_KEY="sk-or-..."
```

> **Migration note**: The legacy `OPENROUTER_API_KEY` is still accepted as a fallback to avoid breaking existing setups, but you will see a deprecation message on use. Please migrate to `OPENROUTER_IMAGE_API_KEY`.

> **Security**: Never store API keys in git-tracked files.

## Models

Any OpenRouter image-generation model is supported — just pass its full `provider/model-id`. Two shorthands are provided for convenience:

| Shorthand | Model ID | Description |
|-----------|----------|-------------|
| `flash` | `google/gemini-2.5-flash-image` | Fast and cost-effective |
| `pro` | `google/gemini-3-pro-image-preview` | Gemini high quality |

Examples of full IDs you can pass directly:

- `black-forest-labs/flux-1.1-pro`
- `google/gemini-2.5-flash-image`
- any other image model listed on OpenRouter

**If you don't specify a model, the skill will ask you to pick one before running.** There is no silent default — every run is an explicit choice.

## Prompt Optimization

If your prompt is short or abstract (e.g., `a cat`, `a beautiful landscape`), the skill will offer to optimize it into a richer visual description — style, lighting, composition, color, mood, detail — while preserving your original subject. You can accept the optimization, keep the original, or edit it yourself.

Already-detailed prompts skip optimization automatically. You can also explicitly ask for it with phrases like "优化 prompt" or "make my prompt better".

## Usage

The skill triggers automatically on keywords like "generate image", "draw", "nano banana", "图像生成", etc.

### Generate an image with an explicit model

```
generate image with pro: a cute cat wearing a space helmet
```

### Let the skill ask you which model to use

```
generate image: a photorealistic mountain landscape at sunset
```

(The skill will prompt you to choose `flash`, `pro`, or a custom model ID.)

### Use a custom OpenRouter model

```
generate image with black-forest-labs/flux-1.1-pro: a neon cityscape at night
```

### Edit an existing image

```
edit image ./photo.png with pro: add a rainbow in the sky
```

## Output

Images are saved to the current directory as `nano-banana-YYYYMMDD-HHMMSS.png`. The run report shows the final prompt, model used, and whether the prompt was optimized.

## Requirements

- `curl` - HTTP requests
- `jq` - JSON parsing
- `base64` - Binary decoding

These tools are pre-installed on most macOS and Linux systems.
