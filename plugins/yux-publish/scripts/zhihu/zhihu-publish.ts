#!/usr/bin/env bun
/**
 * zhihu-publish.ts - 知乎专栏文章发布工具
 *
 * 将 MDX/Markdown 文件转换为知乎兼容的 HTML，支持：
 * - MDX 自定义组件预处理（BlogImage, VideoEmbed, QuoteCard 等）
 * - Markdown → HTML 渲染（使用 marked）
 * - 知乎特定 HTML 后处理
 * - 复制 HTML 到系统剪贴板（macOS）
 * - dry-run 模式输出 JSON 元数据
 *
 * Usage:
 *   npx -y bun zhihu-publish.ts <file> [options]
 *
 * Options:
 *   --title <title>     覆盖标题
 *   --tags <tags>       逗号分隔的话题标签
 *   --copy-html         转换并复制到剪贴板
 *   --dry-run           仅转换，输出 JSON 元数据
 *   --help              显示帮助
 */

import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { spawnSync } from "node:child_process";
import { marked } from "marked";

// ============================================================
// 1. CLI 参数解析
// ============================================================

interface CliArgs {
  filePath: string;
  title?: string;
  tags?: string[];
  copyHtml: boolean;
  dryRun: boolean;
}

function printUsage(): never {
  console.log(`知乎专栏文章发布工具

将 MDX/Markdown 文件转换为知乎兼容的 HTML。

Usage:
  npx -y bun zhihu-publish.ts <file> [options]

Arguments:
  file                MDX (.mdx) 或 Markdown (.md) 文件

Options:
  --title <title>     覆盖标题
  --tags <tags>       逗号分隔的话题标签
  --copy-html         转换并复制 HTML 到系统剪贴板
  --dry-run           仅转换，输出 JSON 元数据
  --help              显示帮助

Frontmatter 字段:
  title               文章标题
  description         文章摘要
  tags                话题标签（YAML 数组）

Example:
  npx -y bun zhihu-publish.ts article.mdx
  npx -y bun zhihu-publish.ts article.mdx --copy-html
  npx -y bun zhihu-publish.ts article.mdx --tags "AI编程,Claude Code" --dry-run
`);
  process.exit(0);
}

function parseArgs(argv: string[]): CliArgs {
  if (argv.length === 0 || argv.includes("--help") || argv.includes("-h")) {
    printUsage();
  }

  const args: CliArgs = {
    filePath: "",
    copyHtml: false,
    dryRun: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]!;
    if (arg === "--title" && argv[i + 1]) {
      args.title = argv[++i];
    } else if (arg === "--tags" && argv[i + 1]) {
      args.tags = argv[++i]!.split(",").map((t) => t.trim()).filter(Boolean);
    } else if (arg === "--copy-html") {
      args.copyHtml = true;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (!arg.startsWith("-")) {
      args.filePath = arg;
    }
  }

  if (!args.filePath) {
    console.error("Error: 需要提供文件路径");
    process.exit(1);
  }

  return args;
}

// ============================================================
// 2. Frontmatter 解析
// ============================================================

interface Frontmatter {
  title?: string;
  description?: string;
  tags?: string[];
  [key: string]: unknown;
}

function parseFrontmatter(content: string): {
  frontmatter: Frontmatter;
  body: string;
} {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, body: content };

  const frontmatter: Frontmatter = {};
  const lines = match[1]!.split("\n");
  let currentKey = "";
  let inArray = false;

  for (const line of lines) {
    const trimmed = line.trim();

    // YAML 数组项: - value
    if (inArray && trimmed.startsWith("- ")) {
      const value = trimmed.slice(2).trim().replace(/^['"]|['"]$/g, "");
      if (Array.isArray(frontmatter[currentKey])) {
        (frontmatter[currentKey] as string[]).push(value);
      }
      continue;
    }

    inArray = false;

    const colonIdx = trimmed.indexOf(":");
    if (colonIdx > 0) {
      const key = trimmed.slice(0, colonIdx).trim();
      let value = trimmed.slice(colonIdx + 1).trim();

      if (value === "" || value === "[]") {
        // 可能是 YAML 数组开始
        currentKey = key;
        frontmatter[key] = [];
        inArray = true;
        continue;
      }

      // 去掉引号
      if (
        (value.startsWith('"') && value.endsWith('"')) ||
        (value.startsWith("'") && value.endsWith("'"))
      ) {
        value = value.slice(1, -1);
      }

      // 内联数组: [a, b, c]
      if (value.startsWith("[") && value.endsWith("]")) {
        frontmatter[key] = value
          .slice(1, -1)
          .split(",")
          .map((v) => v.trim().replace(/^['"]|['"]$/g, ""))
          .filter(Boolean);
      } else {
        frontmatter[key] = value;
      }
      currentKey = key;
    }
  }

  return { frontmatter, body: match[2]! };
}

// ============================================================
// 3. MDX 预处理
// ============================================================

function extractProp(tag: string, propName: string): string {
  // 引号值: prop="value" 或 prop='value'
  const quotedMatch = tag.match(
    new RegExp(`${propName}\\s*=\\s*["']([^"']*)["']`)
  );
  if (quotedMatch) return quotedMatch[1] || "";
  // JSX 表达式: prop={...}
  const exprMatch = tag.match(
    new RegExp(`${propName}\\s*=\\s*\\{([^}]*)\\}`)
  );
  if (exprMatch) return exprMatch[1]?.trim() || "";
  return "";
}

function cleanMarkTags(text: string): string {
  return text.replace(/<\/?mark>/g, "");
}

function preprocessMdx(content: string): string {
  let result = content;

  // 1. BlogImage → ![alt](src) + caption
  result = result.replace(/<BlogImage\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const src = extractProp(tag, "src");
    const alt = extractProp(tag, "alt");
    const caption = extractProp(tag, "caption");
    if (caption) {
      return `![${alt}](${src})\n\n*${caption}*`;
    }
    return `![${alt}](${src})`;
  });

  // 2. VideoEmbed → blockquote
  result = result.replace(/<VideoEmbed\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const url = extractProp(tag, "url");
    const title = extractProp(tag, "title");
    const caption = extractProp(tag, "caption");
    const lines: string[] = [];
    if (title) lines.push(`> **${title}**`);
    if (caption) lines.push(`> ${caption}`);
    lines.push(`> 视频链接: ${url}`);
    return lines.join("\n");
  });

  // 3. QuoteCard → blockquote
  result = result.replace(/<QuoteCard\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const quoteZh = extractProp(tag, "quoteZh");
    const quote = extractProp(tag, "quote");
    const author = extractProp(tag, "author");
    const source = extractProp(tag, "source");
    const text = cleanMarkTags(quoteZh || quote);
    return `> ${text}\n>\n> — ${author}，*${source}*`;
  });

  // 4. ArticleCard → blockquote
  result = result.replace(/<ArticleCard\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const titleZh = extractProp(tag, "titleZh");
    const title = extractProp(tag, "title");
    const url = extractProp(tag, "url");
    const author = extractProp(tag, "author");
    const displayTitle = titleZh || title;
    if (author) {
      return `> **${displayTitle}** — ${author}\n> ${url}`;
    }
    return `> **${displayTitle}**\n> ${url}`;
  });

  // 5. GlossaryCard → blockquote
  result = result.replace(/<GlossaryCard\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const term = extractProp(tag, "term");
    const definition = cleanMarkTags(extractProp(tag, "definition"));
    return `> **${term}**：${definition}`;
  });

  // 6. ProfileCard → bold text
  result = result.replace(/<ProfileCard\s+[\s\S]*?\/\s*>/gs, (tag) => {
    const name = extractProp(tag, "name");
    const role = extractProp(tag, "role");
    const bio = extractProp(tag, "bio");
    let output = `**${name}** — ${role}`;
    if (bio) {
      output += `\n\n${bio}`;
    }
    return output;
  });

  // 7. 移除 JSX 注释: {/* ... */}
  result = result.replace(/\{\/\*[\s\S]*?\*\/\}/g, "");

  // 8. 移除剩余的自闭合 JSX 标签（大写字母开头的组件）
  result = result.replace(/<[A-Z][a-zA-Z]*\s[\s\S]*?\/\s*>/g, "");

  // 9. 移除包裹式 JSX 标签（如 <Callout>...</Callout>）保留内部内容
  result = result.replace(
    /<([A-Z][a-zA-Z]*)[^>]*>([\s\S]*?)<\/\1>/g,
    "$2"
  );

  // 10. 将内部相对链接转为纯文本
  result = result.replace(
    /\[([^\]]+)\]\(\/(blog|docs)\/[^)]*\)/g,
    "$1"
  );

  // 11. 移除 import 语句
  result = result.replace(/^import\s+.+$/gm, "");

  // 12. 移除 export 语句
  result = result.replace(/^export\s+.+$/gm, "");

  // 13. 清理过多空行 (3+ → 2)
  result = result.replace(/\n{3,}/g, "\n\n");

  return result;
}

// ============================================================
// 4. Markdown → HTML 渲染
// ============================================================

function escapeCodeHtml(code: string): string {
  return code
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function renderMarkdown(markdown: string): string {
  const renderer = new marked.Renderer();

  // 自定义代码块渲染（带简单样式）
  renderer.code = function ({ text, lang }: { text: string; lang?: string }) {
    const escaped = escapeCodeHtml(text);
    const langLabel = lang ? `<div style="color:#999;font-size:12px;margin-bottom:4px;">${lang}</div>` : "";
    return `<pre style="background:#f6f8fa;border-radius:6px;padding:1em;overflow-x:auto;margin:1em 0;font-size:14px;line-height:1.6;">${langLabel}<code>${escaped}</code></pre>`;
  };

  marked.setOptions({
    gfm: true,
    breaks: false,
    renderer,
  });

  const html = marked.parse(markdown);
  if (typeof html !== "string") {
    throw new Error("Markdown 渲染失败");
  }
  return html;
}

// ============================================================
// 5. 知乎 HTML 样式与后处理
// ============================================================

const ZHIHU_STYLES = `
/* 知乎文章样式 */
.zhihu-article {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Microsoft YaHei", "Source Han Sans SC", "Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #1a1a1a;
  word-break: break-word;
}
.zhihu-article h1 {
  font-size: 24px;
  font-weight: 700;
  margin: 1.5em 0 0.8em;
  line-height: 1.4;
}
.zhihu-article h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 1.4em 0 0.6em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #e8e8e8;
  line-height: 1.4;
}
.zhihu-article h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 1.2em 0 0.5em;
  line-height: 1.4;
}
.zhihu-article p {
  margin: 0.8em 0;
}
.zhihu-article img {
  max-width: 100%;
  height: auto;
  margin: 1em auto;
  display: block;
  border-radius: 4px;
}
.zhihu-article blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 3px solid #0066ff;
  background: #f6f8fa;
  color: #555;
}
.zhihu-article blockquote p {
  margin: 0.3em 0;
}
.zhihu-article pre {
  background: #f6f8fa;
  border-radius: 6px;
  padding: 1em;
  overflow-x: auto;
  margin: 1em 0;
  font-size: 14px;
  line-height: 1.6;
}
.zhihu-article code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.9em;
}
.zhihu-article :not(pre) > code {
  background: #f0f0f0;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  color: #d63384;
}
.zhihu-article ul, .zhihu-article ol {
  padding-left: 1.5em;
  margin: 0.8em 0;
}
.zhihu-article li {
  margin: 0.3em 0;
}
.zhihu-article table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 14px;
}
.zhihu-article th, .zhihu-article td {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}
.zhihu-article th {
  background: #f6f8fa;
  font-weight: 600;
}
.zhihu-article tr:nth-child(even) {
  background: #fafafa;
}
.zhihu-article a {
  color: #0066ff;
  text-decoration: none;
}
.zhihu-article a:hover {
  text-decoration: underline;
}
.zhihu-article hr {
  border: none;
  border-top: 1px solid #e8e8e8;
  margin: 1.5em 0;
}
.zhihu-article em {
  color: #666;
}
.zhihu-article strong {
  font-weight: 700;
  color: #1a1a1a;
}
`;

function postProcessHtml(html: string): string {
  let result = html;

  // 1. 替换 <section> → <div>
  result = result.replace(/<section([^>]*)>/gi, "<div$1>");
  result = result.replace(/<\/section>/gi, "</div>");

  // 2. 确保所有图片 URL 使用 https://
  result = result.replace(
    /(<img[^>]+src=["'])http:\/\//gi,
    "$1https://"
  );

  // 3. 移除 mac-sign 装饰 SVG
  result = result.replace(
    /<div[^>]*class="[^"]*mac-sign[^"]*"[^>]*>[\s\S]*?<\/div>/gi,
    ""
  );

  // 4. 移除 data-* 属性
  result = result.replace(/ data-[a-z-]+="[^"]*"/gi, "");

  // 5. 图片 + caption 合并为 <figure>
  //    匹配: <p><img ...></p>\n<p><em>caption</em></p>
  result = result.replace(
    /<p>(<img[^>]+>)<\/p>\s*<p><em>([^<]+)<\/em><\/p>/g,
    '<figure>$1<figcaption>$2</figcaption></figure>'
  );

  // 6. 单独的图片也去掉 <p> 包裹，用 <figure> 替代
  result = result.replace(
    /<p>(<img[^>]+>)<\/p>/g,
    '<figure>$1</figure>'
  );

  // 7. 清理多余空行
  result = result.replace(/\n{3,}/g, "\n\n");

  return result;
}

function wrapHtml(bodyContent: string, title: string): string {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(title)}</title>
<style>${ZHIHU_STYLES}</style>
</head>
<body>
<div class="zhihu-article">
${bodyContent}
</div>
</body>
</html>`;
}

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ============================================================
// 6. 剪贴板操作 (macOS)
// ============================================================

function copyHtmlToClipboard(html: string): boolean {
  if (process.platform !== "darwin") {
    console.error("剪贴板复制仅支持 macOS");
    return false;
  }

  // 使用 Swift 通过 AppKit 复制 HTML 到系统剪贴板
  const swiftCode = `
import AppKit

let html = String(data: FileHandle.standardInput.readDataToEndOfFile(), encoding: .utf8)!
let pasteboard = NSPasteboard.general
pasteboard.clearContents()

// 设置 HTML 和纯文本两种格式
if let htmlData = html.data(using: .utf8) {
    pasteboard.setData(htmlData, forType: .html)
}

// 简单的 HTML → 纯文本转换作为备用
if let attrStr = try? NSAttributedString(
    data: html.data(using: .utf8)!,
    options: [.documentType: NSAttributedString.DocumentType.html,
              .characterEncoding: String.Encoding.utf8.rawValue],
    documentAttributes: nil) {
    pasteboard.setString(attrStr.string, forType: .string)
}
`;

  const result = spawnSync("swift", ["-"], {
    input: swiftCode,
    stdio: ["pipe", "pipe", "pipe"],
    env: { ...process.env },
  });

  // 将 HTML 内容传给 stdin
  const result2 = spawnSync("swift", ["-"], {
    input: `
import AppKit
let htmlContent = """
${html.replace(/\\/g, "\\\\").replace(/"""/g, '\\"""')}
"""
let pasteboard = NSPasteboard.general
pasteboard.clearContents()
if let htmlData = htmlContent.data(using: .utf8) {
    pasteboard.setData(htmlData, forType: .html)
    pasteboard.setString(htmlContent, forType: .string)
}
`,
    stdio: ["pipe", "pipe", "pipe"],
  });

  if (result2.status !== 0) {
    // 备选方案: 用 osascript 设置剪贴板 (仅纯文本)
    const osResult = spawnSync("pbcopy", [], {
      input: html,
      stdio: ["pipe", "pipe", "pipe"],
    });
    return osResult.status === 0;
  }

  return true;
}

// ============================================================
// 7. 辅助函数
// ============================================================

function extractTitle(body: string, frontmatter: Frontmatter): string {
  if (frontmatter.title && typeof frontmatter.title === "string") {
    return frontmatter.title;
  }
  // 从内容中提取第一个 H1 或 H2
  const headingMatch = body.match(/^#{1,2}\s+(.+)$/m);
  if (headingMatch) return headingMatch[1]!.trim();
  // 取第一行非空文本
  const firstLine = body.split("\n").find((l) => l.trim());
  return firstLine?.trim().slice(0, 50) || "无标题";
}

function extractDescription(
  body: string,
  frontmatter: Frontmatter
): string {
  if (
    frontmatter.description &&
    typeof frontmatter.description === "string"
  ) {
    return frontmatter.description;
  }
  // 取第一个非标题、非图片的段落
  const lines = body.split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (
      !trimmed ||
      trimmed.startsWith("#") ||
      trimmed.startsWith("!") ||
      trimmed.startsWith("<") ||
      trimmed.startsWith("```") ||
      trimmed.startsWith("---") ||
      trimmed.startsWith("import ") ||
      trimmed.startsWith("export ")
    ) {
      continue;
    }
    // 清理 markdown 格式
    const plain = trimmed
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/\*([^*]+)\*/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .replace(/`([^`]+)`/g, "$1");
    if (plain.length > 10) {
      return plain.slice(0, 120);
    }
  }
  return "";
}

function extractTags(frontmatter: Frontmatter): string[] {
  if (Array.isArray(frontmatter.tags)) {
    return frontmatter.tags.map(String);
  }
  if (typeof frontmatter.tags === "string") {
    return frontmatter.tags
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
  }
  return [];
}

function countImages(html: string): number {
  const matches = html.match(/<img\s/gi);
  return matches ? matches.length : 0;
}

function removeFirstHeading(body: string, title: string): string {
  // 如果正文以 frontmatter title 相同的 H1 开头，去掉避免重复
  const match = body.match(/^(#{1,2})\s+(.+)\n/);
  if (match && match[2]!.trim() === title.trim()) {
    return body.slice(match[0].length);
  }
  return body;
}

// ============================================================
// 8. 主流程
// ============================================================

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  const filePath = path.resolve(args.filePath);
  if (!fs.existsSync(filePath)) {
    console.error(`Error: 文件不存在: ${filePath}`);
    process.exit(1);
  }

  const rawContent = fs.readFileSync(filePath, "utf-8");

  // 解析 frontmatter
  const { frontmatter, body } = parseFrontmatter(rawContent);

  // 确定标题
  const title = args.title || extractTitle(body, frontmatter);

  // 确定摘要
  const description = extractDescription(body, frontmatter);

  // 确定标签
  const tags = args.tags || extractTags(frontmatter);

  // MDX 预处理
  const isMdx =
    filePath.endsWith(".mdx") || filePath.endsWith(".md");
  let processedBody = body;
  if (isMdx) {
    processedBody = preprocessMdx(body);
  }

  // 移除与标题重复的第一个标题
  processedBody = removeFirstHeading(processedBody, title);

  // Markdown → HTML
  const bodyHtml = renderMarkdown(processedBody);

  // 知乎 HTML 后处理
  const processedHtml = postProcessHtml(bodyHtml);

  // 生成完整 HTML（含样式，用于预览）
  const fullHtml = wrapHtml(processedHtml, title);

  // 统计图片数量
  const imageCount = countImages(processedHtml);

  // 写入临时文件
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "zhihu-"));
  const htmlPath = path.join(tmpDir, "article.html");
  const htmlContentPath = path.join(tmpDir, "article-content.html");

  fs.writeFileSync(htmlPath, fullHtml, "utf-8");
  fs.writeFileSync(htmlContentPath, processedHtml, "utf-8");

  // 输出结果 JSON
  const result = {
    title,
    description,
    tags,
    htmlPath,
    htmlContentPath,
    contentLength: processedHtml.length,
    imageCount,
  };

  if (args.dryRun) {
    console.log(JSON.stringify(result, null, 2));
    console.error(`\n[dry-run] HTML 已生成:`);
    console.error(`  预览: ${htmlPath}`);
    console.error(`  内容: ${htmlContentPath}`);
    return;
  }

  if (args.copyHtml) {
    const ok = copyHtmlToClipboard(processedHtml);
    if (ok) {
      console.error("[zhihu-publish] HTML 已复制到剪贴板");
    } else {
      console.error("[zhihu-publish] 剪贴板复制失败");
    }
  }

  // 输出 JSON 到 stdout（供 SKILL.md 工作流消费）
  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error("Error:", err.message || err);
  process.exit(1);
});
