# Interactive Components Handling

微信公众号不支持 React 交互组件（如 React Flow 流程图）。发布前需要将这些组件截图为静态图片。

## 组件映射表

`wechat-api.ts` 中的 `preprocessMdx` 函数包含 `diagramImageMap`，用于将交互组件替换为静态图片：

```typescript
const diagramImageMap: Record<string, string> = {
  'RalphMechanismFlow': 'https://wyx-shanghai.oss-cn-shanghai.aliyuncs.com/2026-03/ralph-mechanism-flow.png',
  'HumanLoopComparison': 'https://wyx-shanghai.oss-cn-shanghai.aliyuncs.com/2026-03/human-loop-comparison.png',
};
```

## 检测未映射组件

扫描 MDX 文件，查找所有自闭合大写组件标签：

```bash
grep -oP '<[A-Z][a-zA-Z]+\s*/>' <mdx_file>
```

排除已知的标准组件（`BlogImage`、`VideoEmbed`、`QuoteCard`、`ArticleCard`、`GlossaryCard`、`ProfileCard`），剩下的就是可能需要截图的交互组件。

对比 `diagramImageMap` 中已有的映射，找出未映射的组件。

## 截图流程（针对未映射组件）

### 1. 确定页面 URL

根据 MDX 文件路径推断页面 URL：
- `content/docs/notes/ralph-wiggum/concept.mdx` → `/docs/notes/ralph-wiggum/concept`
- `content/blog/some-post.mdx` → `/blog/some-post`

### 2. 启动 Dev Server（如未运行）

```bash
# 检查端口是否已占用，找可用端口
PORT=3456 npm run dev
```

### 3. 用 Chrome DevTools MCP 截图

```javascript
// 1. 打开页面
mcp__chrome-devtools__new_page({ url: "http://localhost:<port>/<path>" })

// 2. 等待页面加载后，找到交互组件
// 优先用 data-component 属性定位，否则用 .react-flow 类
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const els = document.querySelectorAll('[data-component]');
    return Array.from(els).map(el => ({
      component: el.dataset.component,
      rect: el.getBoundingClientRect()
    }));
  }`
})

// 3. 隐藏侧边栏和导航，让组件填满可视区域
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    document.querySelectorAll('aside, header, nav').forEach(el => el.style.display = 'none');
    const grid = document.querySelector('.grid.overflow-x-clip, [class*="grid"][class*="overflow"]');
    if (grid) grid.style.cssText = 'display:block;width:100%;padding:0;margin:0;';
    const article = document.querySelector('article');
    if (article) article.style.cssText = 'width:100%;max-width:100%;padding:5px 20px;margin:0;';
  }`
})

// 4. 滚动到组件位置并截图
mcp__chrome-devtools__evaluate_script({
  function: `() => {
    const el = document.querySelector('[data-component="组件名"]');
    el.scrollIntoView({ block: 'start' });
    window.scrollBy(0, -5);
  }`
})
mcp__chrome-devtools__take_screenshot({ filePath: "/tmp/组件名.png" })

// 5. 用 Python 裁剪（DPR=2 时坐标翻倍）
// python3 crop script based on element rect × devicePixelRatio
```

### 4. 检查 PNG gamma 并上传 OSS

```python
# 检查 gAMA 块
import struct
with open('image.png', 'rb') as f:
    # 如果有错误的 gAMA（值≈2.2 而非 0.45455）且无 sRGB/iCCP，需要修复
    # 修复脚本见 CLAUDE.md 中的 fix_png 函数
```

```bash
# 上传到 OSS
aliyun oss cp /tmp/组件名.png oss://wyx-shanghai/$(date +%Y-%m)/<component-kebab-case>.png --endpoint oss-cn-shanghai.aliyuncs.com -f
```

### 5. 更新 diagramImageMap

编辑 `${SKILL_DIR}/scripts/wechat-api.ts`，在 `diagramImageMap` 中新增一行：

```typescript
'NewComponentName': 'https://wyx-shanghai.oss-cn-shanghai.aliyuncs.com/<year-month>/<component-kebab-case>.png',
```

## 注意事项

- 组件上的 `data-component` 属性用于精准定位，新组件应添加此属性
- `devicePixelRatio` 通常为 2（Retina），裁剪坐标需乘以 DPR
- 截图后触发 `window.dispatchEvent(new Event('resize'))` 让 React Flow 重新适配
- OSS URL 必须使用 `https://` 协议
