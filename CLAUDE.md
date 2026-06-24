# Claude Code 使用

## 项目概述

Claude Code 使用教程、技巧记录和实战项目集合。包括「崔浩AI创业」IP 的短视频爆款选题生成 Skill，以及飞书知识库自动归档工具。

## 项目结构

```
├── README.md                    # 项目说明
├── CLAUDE.md                    # 本项目文档（当前文件）
├── 起号策略                     # IP 内容策略与起号方案（参考文档）
├── feishu_wiki.py               # 飞书知识库工具：创建/移动子文档 + 写入内容
│
├── .agents/
│   └── skills/viral-topic-creator/   # 爆款选题生成 Skill
│       ├── SKILL.md                  # Skill 主文件（创作逻辑 + 保存逻辑）
│       ├── references/               # 爆款分析方法论
│       ├── scripts/                  # 工具脚本（预留）
│       └── assets/                   # 资源文件（预留）
│
├── .claude/
│   ├── settings.local.json      # 本地配置文件（飞书 MCP + 权限）
│   └── skills/
│       ├── viral-topic-creator/      # Skill 副本（symlink → .agents）
│       └── find-skills -> ...        # 已安装的社区 skill
│
├── .git/                        # Git 仓库
├── .gitignore                   # Git 忽略规则
└── skills-lock.json             # npx skills 安装记录
```

## 核心工具

| 文件 | 用途 |
|------|------|
| `feishu_wiki.py` | 读取 OAuth token，在飞书知识库创建子文档并写入内容 |
| `起号策略` | IP 人设/内容权重/四段式模型/7天起号结构（参考文档） |

## 自动化流程

```
出选题 → WebSearch 调研 → 四段式创作 10 条 → 自动保存到飞书知识库
```

- Token 缓存：`~/.cc-lark/tokens.json`（OAuth 授权，有效期 2h 自动刷新）
- 目标位置：知识库「01｜内容选题库（核心流量入口）」的子文档
- 权限脚本：`python feishu_wiki.py --title "标题" --content "内容"`

## 使用说明

- 直接在对话中说「出选题」触发 Skill 自动创作
- `feishu_wiki.py` 可单独使用，向知识库写入任意内容
- 如遇 token 过期，执行 `npx -y cc-lark` 重新授权

## Git 约定

- 默认分支：`master`
- 提交信息使用中文描述变更内容
