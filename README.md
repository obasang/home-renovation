# 住宅装修助手 · home-renovation

面向第一次装修的住宅业主。帮你比较装修模式、筛选施工方、看户型方案、审报价和合同，跟踪增项、阶段付款和整改。

## 安装

本项目使用 [Agent Skills 开放规范](https://agentskills.io/specification)。解压发布包或下载仓库，将根目录命名为 `home-renovation`，保留其中的 `SKILL.md` 和 `references/`，再把整个目录放到客户端的项目技能目录下。

| 客户端 | 项目内入口 | 使用方式 |
| --- | --- | --- |
| Codex | `.agents/skills/home-renovation/SKILL.md` | 输入 `$home-renovation` |
| Claude Code | `.claude/skills/home-renovation/SKILL.md` | 输入 `/home-renovation` |
| Cursor | `.agents/skills/home-renovation/SKILL.md` | 在 Agent 的技能列表中选中 `home-renovation` |

安装后，在该项目中打开新会话并调用 `home-renovation`。使用其他支持 Agent Skills 的客户端时，按该客户端的说明安装同一份目录。

查询现行规则、当地行情或具体公司需要联网。如果客户端打不开扫描版报价，可提供相关页的清晰截图或原表。

## 直接试用

- 我是毛坯交付，第一次装修，只能周末到场，想自选瓷砖和洁具。帮我比较全包、半包和独立设计师加工长。
- 我们常一起做饭，周末有六人用餐。按户型图给两个方案，再按我圈出的地方改图。
- 这两份报价哪些项目可以直接比？帮我找漏项，复算已知总价，再列签约前要问的三件事。
- 原台账和新验收记录在附件里。帮我更新净增项、实付和本期应付，并给我一段能发给工长的回复。

如需连续跟进，保存装修台账。换会话时把台账与新凭证一并提供。

## 示例

[比价和跨会话续账示例](examples/README.md) 提供模拟报价、合同摘录、验收凭证、旧台账和预期结果。

[两居室设计示例](examples/design/README.md) 提供可复现的户型、初稿需求及两轮改图反馈。

[销售户型图和圈注改稿示例](examples/sales-plan/README.md) 可以用一张缺尺寸的截图开始设计，再带着上一版方案去新会话改图。

默认面向中国大陆住宅。报价、物业要求和验收依据随地区与项目变化。涉及现场测量和专业判断的事项，由项目对应人员核查。

采用 [MIT 许可证](LICENSE)。
