---
name: arcaea-knowledge
description: Arcaea 音游知识库，涵盖谱面/搭档/剧情/机制等全维度查询。
---

# Arcaea 知识库 Skill

## 概述

Arcaea 音游知识库，包含游戏机制和剧情故事两大独立索引，支持分类查询、章节检索、实体别名、智能搜索等功能。

## 索引结构

### 双索引设计

| 索引 | 文件 | 文档数 | 大小 | 内容 |
|------|------|--------|------|------|
| `mechanic` | `mechanic_kb.json` | 222 条 | 940 KB | 游戏机制、界面、难度、物件等 |
| `story` | `story_kb.json` | 2750 条 | 5.6 MB | 主线/支线剧情、角色故事、世界观 |
| `all` | `knowledge_base.json` | 2972 条 | 6.5 MB | 完整数据（含分类标签） |

### 机制库分类

| 分类 | 数量 | 说明 |
|------|------|------|
| 物件机制 | 153 | 地键、天键、音弧、长条、判定系统 |
| 搭档系统 | 17 | 搭档属性、技能、觉醒 |
| 游玩机制 | 14 | 分数、评级、结算、潜力值 |
| 界面介绍 | 10 | 主界面、选曲、曲包、结算界面 |
| 世界模式 | 9 | 地图、体力、章节 |
| 网络功能 | 8 | 云端同步、好友、排行榜 |
| 难度系统 | 5 | PST/PRS/FTR/ETR/BYD |
| 曲包系统 | 2 | 曲包分类、Memory Archive |
| 排序分类 | 2 | 曲目排序、筛选 |
| 特殊效果 | 2 | 异象、特殊游玩效果 |

### 剧情库章节分布

| 章节 | 数量 | 说明 |
|------|------|------|
| 叙事片段 | 1410 | 无明确标记的叙事文本 |
| 世界观/叙事 | 583 | 世界观说明、背景介绍 |
| 光/对立主线 | 85 | 光与对立相关剧情 |
| 序章/开端 | 81 | 故事开端场景 |
| 主线-其他 | 70 | 其他主线相关 |
| 回忆/过去 | 69 | 回忆场景 |
| 终章/结局 | 69 | 故事结局 |
| 忘却-相关 | 53 | 忘却角色相关 |
| 彩梦-相关 | 47 | 彩梦角色相关 |
| 爱丽丝&坦尼尔 | 43 | 爱丽丝与坦尼尔相关 |
| 战斗/冲突 | 42 | 战斗场景 |
| 命运/抉择 | 38 | 命运抉择场景 |
| 其他角色 | ~100 | 群愿、咲弥、天音、拉格兰等 |

## 文件结构

```
arcaea-knowledge/
├── SKILL.md              # 本文件
├── knowledge_base.json   # 完整知识库 (6.5MB)
├── mechanic_kb.json      # 机制知识库 (940KB)
├── story_kb.json         # 剧情知识库 (5.6MB)
├── aliases.json          # 实体别名映射
└── query.py              # 查询工具
```

## 实体别名

支持常见别名自动映射：

| 标准名 | 别名 |
|--------|------|
| 音弧 | 蛇, arc, Arc, ARC |
| 地键 | tap, Tap, TAP, 地面音符 |
| 天键 | arctap, Arctap, 天空音符 |
| 长条 | hold, Hold, 长音符 |
| Past | PST, pst |
| Present | PRS, prs |
| Future | FTR, ftr |
| Beyond | BYD, byd |
| 潜力值 | ptt, PTT, Potential |
| 世界模式 | World Mode, 爬梯 |
| 光 | Hikari, hikari, 白姬 |
| 对立 | Tairitsu, tairitsu, 黑姬 |

## 使用方法

### 命令行查询

```bash
# 查看可用索引
python query.py --list-indexes

# 查看实体别名
python query.py --list-aliases

# 机制库查询（默认）
python query.py --entity "音弧"
python query.py --search "判定"
python query.py --category "难度系统"

# 别名搜索（"蛇" → "音弧"）
python query.py --entity "蛇"
python query.py --entity "ptt"

# 剧情库查询
python query.py --index story --search "光"
python query.py --index story --chapter "主线-第1章"
python query.py --index story --entity "对立"

# 智能搜索（综合匹配实体+关键词+章节）
python query.py --smart "异象"

# 完整库查询
python query.py --index all --stats

# 三元组搜索
python query.py --subject "音弧" --predicate "俗称"
```

### Python API

```python
from query import load_kb, search_by_keyword, search_by_entity, smart_search

# 加载机制库
kb = load_kb('mechanic')

# 关键词搜索
results = search_by_keyword(kb, "异象", limit=5)

# 实体搜索（支持别名）
results = search_by_entity(kb, "蛇", limit=5)  # 自动映射到"音弧"

# 智能搜索
results = smart_search(kb, "Beyond", limit=5)
```

## 数据格式

每个文档包含以下字段：
- `idx`: 唯一标识符 (SHA256)
- `category`: 分类标签（机制库）
- `chapter`: 章节标签（剧情库）
- `passage`: 原文段落
- `extracted_entities`: 抽取的实体列表
- `extracted_triples`: 三元组关系 [[主语, 谓语, 宾语], ...]

## 优化记录

- 2026-06-09: 自动分类，将 2972 条文档分为 11 个类别
- 2026-06-09: 分离为双索引（机制库 222 条 + 剧情库 2750 条）
- 2026-06-09: 剧情库增加章节标签（按角色/场景/主线分类）
- 2026-06-09: 增加实体别名映射（aliases.json）
- 2026-06-09: 实现智能搜索（综合匹配实体+关键词+章节）
- 原始数据包含 OpenIE 抽取的实体和三元组
