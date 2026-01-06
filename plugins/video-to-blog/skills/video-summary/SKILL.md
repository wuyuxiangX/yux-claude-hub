---
name: video-summary
description: Organize video transcript into structured summary. Triggers: "summarize video", "video summary", "content summary", "organize transcript", "整理视频", "视频摘要", "内容总结".
allowed-tools: Read, Write, Glob, Grep
---

# Video Content Summary

Organize a video transcript file into a structured summary with key points, timeline, and notable quotes. Supports different video types with specialized processing.

Input: Transcript file path or content from $ARGUMENTS

## Step 1: Load Transcript

1. **Identify the transcript file**:
   - If a file path is provided, read that file
   - If no path provided, look for recent `.txt` files in current directory
   - Ask user to specify if multiple transcript files exist

2. **Read and parse the content**:
   - Load the full transcript text
   - Identify if timestamps are present
   - Detect the language (Chinese, English, etc.)
   - Estimate video duration from timestamps (if available)

## Step 2: Identify Video Type

Analyze the transcript to determine the video type:

| Type | Indicators |
|------|------------|
| **Interview** | Multiple speakers, Q&A format, dialogue patterns |
| **Tutorial** | Step-by-step instructions, demonstrations |
| **Talk/Lecture** | Single speaker, educational content |
| **Review** | Product/service evaluation, pros/cons |
| **Podcast** | Casual conversation, multiple hosts |
| **News** | Reporting style, factual delivery |

**Ask user to confirm the detected type** or let them choose if unclear.

## Step 3: Extract Key Information

### For ALL video types:

1. **Identify main topics**:
   - What is the video about?
   - What are the major themes discussed?
   - Who are the speakers (if identifiable)?

2. **Extract key points**:
   - Main arguments or ideas
   - Important facts or statistics
   - Conclusions or recommendations

3. **Create timeline highlights**:
   - Key moments with timestamps (if available)
   - Topic transitions
   - Important demonstrations or examples

### For INTERVIEW/PODCAST types (additional processing):

4. **Identify speakers**:
   - Detect speaker changes in transcript
   - Label speakers (Host, Guest, Speaker A/B, or by name if mentioned)
   - Note each speaker's role/expertise if mentioned

5. **Extract dialogue segments**:
   - Important Q&A exchanges
   - Key discussion points
   - Controversial or insightful moments

6. **Translate dialogue** (if original is not in user's preferred language):
   - Preserve original text
   - Provide translation below each segment
   - Maintain speaker labels

## Step 4: Generate Structured Summary

### Standard Output (for Tutorial/Talk/Review/News):

```markdown
# Video Summary: [Title]

## Overview
- **Type**: [Tutorial/Talk/Review/News]
- **Duration**: [estimated duration]
- **Language**: [detected language]
- **Main Topic**: [brief description]
- **Key Themes**: [list of themes]

## Executive Summary
[2-3 paragraph summary of the entire video content]

## Key Points

### [Topic 1]
- Point 1
- Point 2
- Point 3

### [Topic 2]
- Point 1
- Point 2

## Timeline Highlights
- [00:00] Introduction and context
- [05:30] Main argument begins
- [15:00] Key demonstration
- [25:00] Conclusion and takeaways

## Notable Quotes
> "Quote 1" - [Speaker/Context]

> "Quote 2" - [Speaker/Context]

## Key Takeaways
1. Takeaway 1
2. Takeaway 2
3. Takeaway 3
```

### Interview/Podcast Output (enhanced format):

```markdown
# Video Summary: [Title]

## 📋 Basic Info

| Item | Content |
|------|---------|
| 📺 Video | [Platform](URL) |
| 🎙️ Host | [Host Name] ([Show/Channel Name]) |
| 💡 Guest | [Guest Name] ([Title/Company]) |
| 📝 Topics | Topic1, Topic2, Topic3 |
| ⏱️ Duration | [estimated duration] |

---

## 📝 Executive Summary

[2-3 paragraph summary of the entire conversation]

---

## 👥 Participants

### 🎙️ Host: [Name]
[Brief background about the host]

### 💡 Guest: [Name]
[Brief background, expertise, why they were invited]

---

## 🎯 Key Discussion Points

### Topic 1: [Topic Title]
**Summary**: [Brief summary of this discussion segment]

**Key Insights**:
- Insight 1
- Insight 2

### Topic 2: [Topic Title]
**Summary**: [Brief summary]

**Key Insights**:
- Insight 1
- Insight 2

---

## 🗣️ Interview Dialogue

### 🎙️ Host Opening

> **English:** Original English text here. This is the host's opening remarks or question...

**中文：** 这里是中文翻译内容。这是主持人的开场白或问题...

---

### 💡 [Guest Name]

> **English:** Guest's response in original language. Their insights, opinions, and explanations...

**中文：** 嘉宾的回应翻译。他们的见解、观点和解释...

---

### 🎙️ Host Follow-up

> **English:** Host's follow-up question or comment...

**中文：** 主持人的后续问题或评论...

---

### 💡 [Guest Name]

> **English:** Guest's continued response...

**中文：** 嘉宾的继续回应...

---

## 💬 Notable Quotes

### 💡 [Guest Name]
> **English:** "Notable quote in original language..."

**中文：** "值得注意的引用翻译..."

### 🎙️ [Host Name]
> **English:** "Another notable quote..."

**中文：** "另一个值得注意的引用..."

---

## 🎯 Key Takeaways

1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

---

## 📚 Recommendations Mentioned

[If the guest mentioned any books, tools, resources, etc.]
- 📖 Book: [Title] by [Author]
- 🔧 Tool: [Tool Name]
- 🔗 Resource: [Resource Name]
```

### Talk/Lecture Output (enhanced format):

```markdown
# Video Summary: [Title]

## 📋 Basic Info

| Item | Content |
|------|---------|
| 📺 Video | [Platform](URL) |
| 🎤 Speaker | [Speaker Name] ([Title/Affiliation]) |
| 🏛️ Event | [Conference/Event Name] (if applicable) |
| 📝 Topic | [Main Topic] |
| ⏱️ Duration | [estimated duration] |

---

## 📝 Executive Summary

[2-3 paragraph summary of the entire talk]

---

## 🎤 About the Speaker

### [Speaker Name]
[Brief background, expertise, notable achievements, why this person is qualified to speak on this topic]

---

## 🎯 Core Arguments

### Main Thesis
[The central argument or message of the talk]

### Supporting Arguments
1. **Argument 1**: [Description]
2. **Argument 2**: [Description]
3. **Argument 3**: [Description]

---

## 📑 Talk Structure

### 1. Introduction [00:00]
[What the speaker sets up in the opening]

### 2. [Section Title] [05:00]
[Key points covered in this section]

### 3. [Section Title] [15:00]
[Key points covered in this section]

### 4. Conclusion [25:00]
[How the speaker wraps up, call to action if any]

---

## 💡 Key Insights (with Translation)

### Insight 1: [Topic]

> **English:** Original quote or passage from the speaker explaining this insight...

**中文：** 演讲者解释这个观点的原文翻译...

---

### Insight 2: [Topic]

> **English:** Another important passage...

**中文：** 另一段重要内容的翻译...

---

### Insight 3: [Topic]

> **English:** Key argument or evidence presented...

**中文：** 关键论点或证据的翻译...

---

## 💬 Notable Quotes

### 🎤 [Speaker Name]
> **English:** "A memorable quote from the talk..."

**中文：** "演讲中令人难忘的引用翻译..."

---

> **English:** "Another impactful statement..."

**中文：** "另一个有影响力的陈述翻译..."

---

## 📊 Data & Evidence Mentioned

[If the speaker referenced any statistics, studies, or evidence]
- 📈 [Statistic/Data point]
- 📚 [Study/Research referenced]
- 📋 [Case study mentioned]

---

## 🎯 Key Takeaways

1. Takeaway 1
2. Takeaway 2
3. Takeaway 3

---

## 📚 References & Resources

[Books, papers, tools, or resources mentioned by the speaker]
- 📖 Book: [Title] by [Author]
- 📄 Paper: [Title]
- 🔗 Resource: [Name](URL)

---

## 🤔 Questions Raised

[Questions the speaker posed or left for the audience to consider]
1. [Question 1]
2. [Question 2]
```

## Step 5: Save Summary

1. **Save the summary file**:
   - Filename: `<Original Name>-summary.md`
   - Location: Same directory as the transcript

2. **Report completion**:
   - Summary file path
   - Video type detected
   - Number of speakers identified (for interview type)
   - Number of dialogue segments extracted
   - Languages detected

## Output Quality Guidelines

- **Be concise**: Focus on essential information
- **Be accurate**: Only include information present in the transcript
- **Be structured**: Use clear hierarchical organization
- **Be objective**: Summarize without adding personal opinions
- **Preserve context**: Maintain important nuances from the original
- **Translation quality**: Ensure translations are natural and accurate

## Error Handling

- **Empty transcript**: Notify user the file is empty
- **Unreadable content**: Report parsing issues
- **Too short**: Warn if transcript is too brief for meaningful summary
- **Unknown language**: Ask user to specify the source language
- **Speaker detection failed**: Fall back to "Speaker A/B" labels
