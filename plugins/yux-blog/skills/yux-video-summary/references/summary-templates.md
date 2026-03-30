# Video Summary Output Templates

## SINGLE_FILE Mode (same language)

**Filename**: `<Title>-summary-<lang>.md`

```markdown
# Video Summary: [Title]

## Overview
| Item | Content |
|------|---------|
| Type | [Type] |
| Duration | [Duration] |
| Language | [Language] |
| Topics | [Topics] |
| Speakers | [Speakers] (if applicable) |

## Executive Summary
[2-3 paragraphs in user_language]

## Key Points
### [Topic 1]
- Point 1
- Point 2

### [Topic 2]
- Point 1

## Timeline
- [00:00] [Description]
- [05:30] [Description]

## Notable Quotes
> "Quote 1" - [Speaker]

> "Quote 2" - [Speaker]

## Key Takeaways
1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

## Resources Mentioned
- [Book/Tool/Link]

---

# Organized Transcript

> Fillers removed, organized by topic.

## [00:00] Introduction
[Cleaned content...]

## [05:30] [Topic Title]
[Cleaned content...]

## Closing
[Cleaned content...]
```

## DUAL_FILE Mode (different languages)

**File 1**: `<Title>-summary-<user_lang>.md`

```markdown
# Video Summary: [Title]

> Original language: [video_lang], Summary language: [user_lang]
> Organized transcript: `<Title>-transcript-<video_lang>.md`

## Overview
[Same structure as SINGLE_FILE, content in user_language]

## Executive Summary
[In user_language]

## Key Points
[In user_language]

## Timeline
[Descriptions in user_language]

## Notable Quotes
> "[Original quote in video_language]"
> *Translation: [Translation in user_language]*

## Key Takeaways
[In user_language]

## Related Files
- Organized transcript: `<Title>-transcript-<video_lang>.md`
```

**File 2**: `<Title>-transcript-<video_lang>.md`

```markdown
# Organized Transcript: [Title]

> Fillers removed, organized by topic. Original language preserved.

## Metadata
| Item | Value |
|------|-------|
| Language | [video_lang] |
| Duration | [Duration] |
| Speakers | [Speakers] |

## [00:00] Introduction
[Cleaned original content...]

## [05:30] [Topic Title]
[Cleaned original content...]

## Closing
[Cleaned original content...]
```
