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

## 安装方法

### 作为 AstrBot Skill 安装

```bash
git clone https://github.com/Blueteemo/arcaea-knowledge-skill.git
# 将 arcaea-knowledge-skill 目录放到 AstrBot 的 skills 目录下
# 重启 AstrBot 即可自动加载
```

### 依赖安装

```bash
pip install -r requirements.txt
# 或手动安装所需依赖
```

## 功能特性

### 🎮 歌曲查询
- 按曲名、艺术家、分类、别名查询曲目信息
- 查询难度定数、谱面类型（PST/PRS/FTR/ETR/BYD）
- 别名智能映射（"绿魔王"→"Cyaegha"）

### 🎭 剧情检索
- 按角色（光、对立、忘却、彩梦等）检索剧情
- 按章节（主线、支线、角色故事）浏览
- 全文搜索剧情对话

### ⚙️ 机制查询
- 查询游戏系统（音弧、地键、天键、长条等）
- 查询潜力值（ptt）计算规则
- 查询世界模式、异象触发条件等

### 🔍 别名搜索
- 支持自然别名的自动映射
- 如"蛇"→"音弧"、"ptt"→"潜力值"

## 使用示例

群聊问法：
- "绿魔王是什么歌？"
- "光和对立的剧情介绍一下"
- "Beyond难度是什么意思"
- "音弧的判定规则是什么"
- "蛇是什么机制"
- "潜力值怎么算的"

命令行查询：

```bash
# 查看可用索引
python query.py --list-indexes
...

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
