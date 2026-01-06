---
name: blog-writer
description: Generate blog article from video summary. Triggers: "write blog", "generate article", "create post", "blog from video", "写博客", "生成文章", "写文章".
allowed-tools: Read, Write, Glob, Grep
---

# Blog Article Generator

Transform a video summary into a polished blog article with engaging writing and proper structure.

Input: Summary file path or content from $ARGUMENTS

## Step 1: Load Source Content

1. **Identify the source file**:
   - If a file path is provided, read that file
   - If no path provided, look for recent `*-summary.md` files
   - Ask user to specify if multiple summary files exist

2. **Parse the summary**:
   - Extract key points
   - Identify main themes
   - Note important quotes
   - Understand the overall message

## Step 2: Choose Writing Style

**Ask user to select a writing style**:

1. **Technical Blog** (专业深入)
   - In-depth analysis
   - Professional terminology
   - Detailed explanations
   - Code examples if relevant
   - Target: Technical professionals

2. **Casual Explainer** (通俗易懂)
   - Conversational tone
   - Simple language
   - Analogies and examples
   - Accessible to beginners
   - Target: General audience

3. **News Style** (客观简洁)
   - Objective reporting
   - Concise paragraphs
   - Fact-focused
   - Minimal commentary
   - Target: Quick readers

Wait for user selection before proceeding.

## Step 3: Generate Article Structure

Based on the chosen style, create an outline:

### For Technical Blog:
```
1. Introduction (problem statement)
2. Background/Context
3. Main Content (detailed sections)
4. Technical Deep Dive
5. Practical Applications
6. Conclusion
7. References/Resources
```

### For Casual Explainer:
```
1. Hook (engaging opening)
2. Why This Matters
3. The Main Story
4. Key Insights (simplified)
5. What You Can Do
6. Wrap Up
```

### For News Style:
```
1. Lead (who, what, when, where, why)
2. Key Facts
3. Supporting Details
4. Expert Quotes
5. Conclusion
```

## Step 4: Write the Article

Generate the full article following these guidelines:

### Title
- Create an engaging, SEO-friendly title
- Should reflect the main topic
- Consider using numbers or questions for engagement

### Introduction
- Hook the reader immediately
- State what they will learn
- Keep it concise (2-3 paragraphs max)

### Body
- Use clear section headings
- Break into digestible paragraphs
- Include relevant quotes from the video
- Add transitions between sections
- Use bullet points for lists

### Conclusion
- Summarize key takeaways
- Provide actionable insights
- End with a thought-provoking statement or call-to-action

### Formatting
- Use Markdown formatting
- Include proper heading hierarchy (H1, H2, H3)
- Add emphasis where appropriate (bold, italic)
- Keep paragraphs short (3-5 sentences)

## Step 5: Add Metadata

Include at the top of the article:

```markdown
---
title: [Generated Title]
date: [Current Date]
source: [Original Video Title/URL if known]
tags: [relevant, tags, here]
---
```

## Step 6: Quality Check

Before saving, ensure:

- [ ] Title is engaging and accurate
- [ ] Introduction hooks the reader
- [ ] Content flows logically
- [ ] Key points from video are covered
- [ ] No factual errors introduced
- [ ] Proper grammar and spelling
- [ ] Consistent tone throughout
- [ ] Appropriate length for the style

## Step 7: Save Article

1. **Generate filename**:
   - Format: `YYYY-MM-DD-[slug-from-title].md`
   - Example: `2024-01-15-how-to-build-ai-agents.md`

2. **Save the file** to current directory

3. **Report completion**:
   - File path
   - Word count
   - Estimated reading time
   - Writing style used

## Output Example

```markdown
---
title: "Building AI Agents: A Complete Guide"
date: 2024-01-15
source: "YouTube - Tech Talk Episode 42"
tags: [AI, agents, tutorial, development]
---

# Building AI Agents: A Complete Guide

Have you ever wondered how AI agents actually work? In this comprehensive guide...

## Why AI Agents Matter

The landscape of artificial intelligence is rapidly evolving...

## Getting Started

Before diving into the technical details...

[... rest of article ...]

## Conclusion

Building AI agents is no longer just for research labs...

---
*This article was generated from video content.*
```

## Error Handling

- **No summary available**: Ask user to run video-summary first
- **Incomplete content**: Warn about potentially thin article
- **Style not selected**: Default to Casual Explainer after timeout
