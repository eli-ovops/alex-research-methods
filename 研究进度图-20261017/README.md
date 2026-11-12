# 研究进度图交付 · 2026-10-17

三张 PNG 均 1600×1100；确定性 SVG 文字排版，以既有 bundled Node + sharp/libvips 渲染。没有安装或下载依赖。未运行研究模型、训练、回测、交易或访问账户。只写本目录。

## 文件用途
- 01-goal-roadmap.png / .svg：目标与五阶段路线；SVG 为可检索编辑源。
- 02-evidence-results.png / .svg：训练/旧封存测试相对基准的 MSE 对照。
- 03-blockers-decision.png / .svg：已核事项、未决问题和当前决策。
- index.html：三图内嵌 SVG 总览，支持适应宽度与原尺寸，附精确值与阅读边界。
- render.mjs：完整可重生成图源，仅生成本目录图件。
- manifest.json：最终图片、图源、HTML与脚本的字节和 SHA256。
- README.md：本交付与视觉验收记录。

## 来源与验收
内容核对指定的2026-10-17训练前向诊断、失败诊断报告；2026-10-16综合报告仅取目标与机制，未复活旧实验建议。没有重新计算研究指标；MSE倍数显示两位小数。三张PNG已用view_image逐一实看，中文正常、数字可读、无明显裁切或重叠；根PMO亦已审首版。根要求两处文案修改后，图2/3再次实际查看，无新增版面问题。

主内容字号约28–52px，脚注23px；聊天窄栏可能需打开原图或总览放大。SVG依赖本机中文字体，PNG为已固定像素交付。HTML未做跨浏览器验收。

所读规则：PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-13-v4、§4文件与证据；show-me技能。目标gpt-6-astra/medium；实际model、effort、速度模式UNKNOWN。

工具限制：首次sharp旧入口lib/index.js不存在，已定向查询LOCAL_BLOCKERS并按本机package.json的dist/index.mjs修正。无系统配置变更。所有文件均为交付、复现或证据用途，全部保留，无待清理一次性文件。
