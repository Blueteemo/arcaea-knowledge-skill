# 🎵 Arcaea 知识库

Arcaea 机制与剧情段落检索工具，支持分类、章节、实体别名和三元组查询。不是完整歌曲目录、谱面定数数据库或自然语言问答模型。

## 安装与使用

需要 Python 3.10 或以上版本，仅使用标准库，无需安装依赖。

```bash
git clone https://github.com/Blueteemo/arcaea-knowledge-skill.git
cd arcaea-knowledge-skill
python query.py --list-indexes
python query.py --entity "蛇"
python query.py --entity "ptt"
python query.py --entity "ETR"
python query.py --smart "异象"
python query.py --index story --chapter "主线-第1章"
python query.py --index story --entity "对立"
python query.py --index all --stats
python query.py --subject "音弧" --predicate "简称"
```

作为 AstrBot Skill 使用时，将整个目录放入其 skills 目录，按 AstrBot 的技能加载方式加载 SKILL.md。

## 数据与检索边界

| 索引 | 文件 | 条数 | 内容 |
|---|---|---:|---|
| mechanic（默认） | mechanic_kb.json | 225 | 机制、界面、搭档系统、世界模式 |
| story | story_kb.json | 2747 | 剧情段落、故事解锁说明与角色叙事 |
| all | knowledge_base.json | 2972 | 完整库，作为正文和分类的主数据 |

- `--search` 是原文关键词子串检索，不扩展别名。
- `--entity` 精确匹配抽取实体及其别名；模糊匹配使用 `--smart`。
- `--smart` 对全索引匹配结果排序，但不理解自然语言问题；应提炼关键词。
- `--chapter` 匹配已有章节标签。标签来自历史自动分类，不保证连续、完整或顺序正确。
- 三元组主语／宾语使用实体别名，谓语使用关系别名；抽取结果应回到原文核验。
- 未找到结果不代表游戏不存在该内容。歌曲名称在原文中出现，不代表具有歌曲属性或定数数据；不提供“绿魔王”等歌曲别名映射。

## 来源与时效

历史 README 声明原文整理自 Arcaea Wiki，实体及三元组由 OpenIE 抽取。但仓库没有保留具体站点 URL、页面修订号、采集时间、授权记录或目标游戏版本；这些信息均未知，不能补写推测值。

分库原有 `meta.updated = 2026-06-09` 是整理日期，不等于原文采集日期或游戏版本。2026-10-04 本轮只修复查询、校正三条明确误分类，未抓取新内容；不声称与当前版本同步。保留原文、实体、三元组和所有记录 ID。

后续导入应逐条记录来源 URL、页面修订号（如可取得）、采集时间、游戏版本（如可确认）及使用许可，并核验移动版／NS 版差异。缺失信息明确标记未知，不以维护日期替代。

## 维护与校验

rebuild_indexes.py 从完整库重建分库，保留已有剧情章节标签并应用三条已核验的分类修正；它不是联网同步脚本。新剧情没有标签时标为“未分类”，需要人工校对。不要只修改分库中的正文或分类。

```bash
python rebuild_indexes.py
python rebuild_indexes.py --check
python -m unittest discover -s tests -v
git diff --check
```

提交前检查分库是否互斥、并集是否与完整库逐字段一致，并确认正文没有意外改动。测试覆盖数据结构、别名、全量搜索排序、跨目录调用和重建一致性；GitHub Actions 在推送及 PR 上执行。

## Python API

```python
from query import load_kb, search_by_entity, smart_search

kb = load_kb('mechanic')
results = search_by_entity(kb, '蛇', limit=5)
results = smart_search(kb, 'Beyond', limit=5)
```

检索注意事项见 SKILL.md，别名配置见 aliases.json。
