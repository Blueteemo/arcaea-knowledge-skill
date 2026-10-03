---
name: arcaea-knowledge
description: 检索 Arcaea 游戏机制、搭档系统与剧情段落。用于音弧判定、潜力值、世界模式、角色故事或已有章节查询；不提供完整歌曲目录、谱面定数或实时版本信息。
---

# Arcaea 知识库

## 选择索引

| 索引 | 文件 | 条数 | 用途 |
|---|---|---:|---|
| mechanic（默认） | mechanic_kb.json | 225 | 机制、界面、搭档系统、世界模式 |
| story | story_kb.json | 2747 | 剧情、故事解锁说明、角色叙事 |
| all | knowledge_base.json | 2972 | 跨索引检索与完整数据 |

## 查询步骤

1. 将问题提炼为实体或关键词，避免直接把完整问题交给子串搜索。
2. 选择机制或剧情索引；无结果时改用 all、标准实体名或更短关键词。
3. 阅读返回的 passage，用原文核验实体和三元组，不要仅凭抽取关系作答。
4. 优先检索明确章节标签。把按角色／场景自动分类的标签视为辅助信息，不当作官方章节结构；不要按返回顺序拼接完整故事。
5. 区分移动版与 NS 版。遇到需要最新版本、定数或曲目完整性的提问，说明本库无法确认，另查可核验来源，不要编造缺失数据。

在本技能目录执行（或用 query.py 的绝对路径执行）：

```bash
python query.py --list-indexes
python query.py --list-aliases
python query.py --entity "蛇"
python query.py --entity "ptt"
python query.py --entity "ETR"
python query.py --search "判定"
python query.py --category "难度系统"
python query.py --smart "异象"
python query.py --index story --chapter "主线-第1章"
python query.py --index story --entity "对立"
python query.py --index all --stats
python query.py --subject "音弧" --predicate "简称"
```

`--entity` 精确匹配实体及别名；`--search` 只匹配原文关键词；`--smart` 综合实体子串、原文和章节匹配，对全索引排序；`--chapter` 对标签作子串匹配。`--limit` 必须是正整数。命令返回检索结果，不是完整自然语言答案。

实体别名包括“蛇／arc→音弧”“ptt→潜力值”“ETR→Eternal”“Hikari→光”“Tairitsu→对立”；完整映射见 aliases.json。谓语别名独立使用其中的 relations，例如“简称→俗称”。不要假设存在歌曲别名映射。

## 数据与时效限制

每条记录包含 idx、category、passage、extracted_entities 和 extracted_triples；剧情分库另有 chapter。idx 是历史 64 位十六进制标识，不因修分类重新生成。

历史资料声明来源为 Arcaea Wiki，但具体站点／页面 URL、修订号、采集时间、许可和游戏版本未保留，均无法确认。meta.updated = 2026-06-09 只是历史整理日期。2026-10-04 修复查询并校正三条误分类，未更新原文或抓取新版本内容。

不要声称本库覆盖当前版本或完整剧情，也不要把歌曲在故事解锁条件中的提及视为歌曲／谱面数据库。回答剧情问题时尊重用户要求，必要时提示剧透。

## 维护

修改正文／分类时以 knowledge_base.json 为主数据，保留 ID。运行 `python rebuild_indexes.py` 重建分库，保留既有剧情标签，再运行 `python rebuild_indexes.py --check` 和 `python -m unittest discover -s tests -v`。新增剧情未归类时保持“未分类”，不要推测章节。

查看 README.md 了解安装、来源缺口与后续导入要求。仅使用 Python 标准库，无需安装依赖。
