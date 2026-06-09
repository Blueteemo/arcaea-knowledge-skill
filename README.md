# 🎵 Arcaea 知识库 — arcaea-knowledge-skill

Arcaea 音游知识库，涵盖谱面/搭档/剧情/机制等全维度查询。

## 文件结构

```
arcaea-knowledge-skill/
├── SKILL.md              # Skill 定义文件
├── README.md             # 本文件
├── .gitignore            # Git 忽略规则
├── aliases.json          # 实体别名映射
├── knowledge_base.json   # 完整知识库（2972条，6.5MB）
├── mechanic_kb.json      # 机制知识库（222条）
├── story_kb.json         # 剧情知识库（2750条）
└── query.py              # 查询脚本
```

## 知识库架构

### 双索引设计

| 索引 | 文件 | 文档数 | 内容 |
|------|------|--------|------|
| `mechanic` | `mechanic_kb.json` | 222 条 | 游戏机制、界面、难度、物件等 |
| `story` | `story_kb.json` | 2750 条 | 主线/支线剧情、角色故事、世界观 |
| `all` | `knowledge_base.json` | 2972 条 | 完整数据（含分类标签） |

### 查询方式

```bash
# 机制查询（默认）
python query.py --entity "音弧"
python query.py --search "判定"

# 剧情查询
python query.py --index story --search "光"
python query.py --index story --chapter "主线-第1章"

# 智能搜索
python query.py --smart "异象"

# 别名搜索
python query.py --entity "蛇"  # 自动映射为"音弧"
python query.py --entity "ptt"  # 自动映射为"潜力值"
```

## 数据来源

知识库基于 Arcaea Wiki 内容整理，使用 OpenIE 抽取实体和三元组关系。
