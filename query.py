#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arcaea 知识库查询工具 - 双索引+别名+章节版"""

import json
import argparse
import sys
import os

# 索引配置
INDEXES = {
    'mechanic': {
        'file': 'mechanic_kb.json',
        'name': '机制知识库',
        'desc': '游戏机制、界面、难度、物件等'
    },
    'story': {
        'file': 'story_kb.json',
        'name': '剧情知识库',
        'desc': '主线/支线剧情、角色故事、世界观'
    },
    'all': {
        'file': 'knowledge_base.json',
        'name': '完整知识库',
        'desc': '包含机制和剧情的完整数据'
    }
}

# 全局别名映射
_ALIASES = None

def load_aliases():
    """加载实体别名映射"""
    global _ALIASES
    if _ALIASES is not None:
        return _ALIASES
    
    alias_path = os.path.join(os.path.dirname(__file__), 'aliases.json')
    if os.path.exists(alias_path):
        with open(alias_path, 'r', encoding='utf-8') as f:
            _ALIASES = json.load(f)
    else:
        _ALIASES = {"entities": {}, "relations": {}}
    return _ALIASES

def expand_entity(entity, kind='entities'):
    """扩展实体别名，返回所有可能的匹配形式"""
    aliases = load_aliases()
    entity_lower = entity.lower()
    variants = {entity, entity_lower}
    
    # 检查是否是某个标准实体的别名
    for standard, alias_list in aliases.get(kind, {}).items():
        if entity_lower == standard.lower() or entity_lower in [a.lower() for a in alias_list]:
            variants.add(standard)
            variants.update(alias_list)
    
    return variants

def load_kb(index='mechanic'):
    """加载指定索引"""
    if index not in INDEXES:
        raise ValueError(f"未知索引: {index}. 可用: {', '.join(INDEXES.keys())}")
    
    kb_path = os.path.join(os.path.dirname(__file__), INDEXES[index]['file'])
    with open(kb_path, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def search_by_category(kb, category, limit=10):
    """按分类搜索"""
    if limit <= 0 or not category.strip():
        return []
    results = [d for d in kb['docs'] if d.get('category') == category]
    return results[:limit]

def search_by_chapter(kb, chapter, limit=10):
    """按章节搜索（剧情库）"""
    if limit <= 0 or not chapter.strip():
        return []
    results = []
    chapter_lower = chapter.lower()
    for doc in kb['docs']:
        doc_chapter = doc.get('chapter', '')
        if chapter_lower in doc_chapter.lower():
            results.append(doc)
        if len(results) >= limit:
            break
    return results[:limit]

def search_by_entity(kb, entity, limit=10):
    """按实体搜索（支持别名）"""
    if limit <= 0 or not entity.strip():
        return []
    results = []
    variants = {v.lower() for v in expand_entity(entity)}
    
    for doc in kb['docs']:
        entities = doc.get('extracted_entities', [])
        for e in entities:
            e_lower = e.lower()
            # 实体搜索采用精确别名匹配；模糊匹配请使用 smart_search。
            if e_lower in variants:
                results.append(doc)
                break
        if len(results) >= limit:
            break
    return results[:limit]

def search_by_keyword(kb, keyword, limit=10):
    """关键词全文搜索"""
    if limit <= 0 or not keyword.strip():
        return []
    results = []
    keyword_lower = keyword.lower()
    for doc in kb['docs']:
        text = doc['passage'].lower()
        if keyword_lower in text:
            results.append(doc)
        if len(results) >= limit:
            break
    return results[:limit]

def search_by_triple(kb, subject=None, predicate=None, object_=None, limit=10):
    """按三元组搜索"""
    if limit <= 0 or not any(v and v.strip() for v in (subject, predicate, object_)):
        return []
    results = []
    subj_variants = expand_entity(subject) if subject else None
    pred_variants = expand_entity(predicate, 'relations') if predicate else None
    obj_variants = expand_entity(object_) if object_ else None
    
    for doc in kb['docs']:
        for triple in doc.get('extracted_triples', []):
            if len(triple) != 3:
                continue
            s, p, o = triple
            match = True
            
            if subj_variants and not any(v.lower() in s.lower() for v in subj_variants):
                match = False
            if pred_variants and not any(v.lower() in p.lower() for v in pred_variants):
                match = False
            if obj_variants and not any(v.lower() in o.lower() for v in obj_variants):
                match = False
            
            if match:
                results.append(doc)
                break
        if len(results) >= limit:
            break
    return results[:limit]

def smart_search(kb, query, limit=10):
    """智能搜索：同时匹配实体、关键词、章节"""
    if limit <= 0 or not query.strip():
        return []
    results = []
    query_lower = query.lower()
    scores = {}
    variants = {v.lower() for v in expand_entity(query)}
    
    for doc in kb['docs']:
        score = 0
        text = doc['passage'].lower()
        
        # 关键词匹配（标题/开头权重更高）
        if query_lower in text:
            score += 10
            # 如果在开头出现，加分
            if text.startswith(query_lower):
                score += 5
        
        # 实体匹配
        entities = [e.lower() for e in doc.get('extracted_entities', [])]
        for e in entities:
            if any(v in e for v in variants):
                score += 20
        
        # 章节匹配（剧情库）
        chapter = doc.get('chapter', '').lower()
        if query_lower in chapter:
            score += 15
        
        if score > 0:
            scores[doc['idx']] = score
            results.append(doc)
        
    
    # 按分数排序
    results.sort(key=lambda d: scores.get(d['idx'], 0), reverse=True)
    return results[:limit]

def format_result(doc, max_length=200):
    """格式化输出结果"""
    text = doc['passage'][:max_length]
    if len(doc['passage']) > max_length:
        text += "..."
    entities = ', '.join(doc.get('extracted_entities', [])[:5])
    category = doc.get('category', '未分类')
    chapter = doc.get('chapter', '')
    
    prefix = f"[{category}]"
    if chapter and chapter != "未分类":
        prefix = f"[{category}|{chapter}]"
    
    return f"""
{prefix} {text}
  实体: {entities}
  ID: {doc['idx'][:16]}...
"""

def main():
    # 只在命令行入口配置输出；导入 Python API 时不改动调用方 stdout。
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(
        description='Arcaea 知识库查询工具 (双索引+别名+章节)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 机制查询（默认索引）
  python query.py --entity "音弧"
  python query.py --search "判定"
  python query.py --category "难度系统"
  
  # 剧情查询
  python query.py --index story --search "光"
  python query.py --index story --chapter "主线-第1章"
  
  # 别名搜索（"蛇" → "音弧"）
  python query.py --entity "蛇"
  
  # 智能搜索（综合匹配）
  python query.py --smart "异象"
  
  # 三元组搜索
  python query.py --subject "音弧" --predicate "俗称"
        """
    )
    
    parser.add_argument('--index', '-i', choices=['mechanic', 'story', 'all'],
                        default='mechanic',
                        help='选择索引 (默认: mechanic)')
    parser.add_argument('--category', '-c', help='按分类查询')
    parser.add_argument('--chapter', '-ch', help='按章节查询（剧情库）')
    parser.add_argument('--entity', '-e', help='按实体查询（支持别名）')
    parser.add_argument('--search', '-s', help='关键词搜索')
    parser.add_argument('--smart', '-sm', help='智能搜索（综合匹配）')
    parser.add_argument('--subject', help='三元组主语')
    parser.add_argument('--predicate', help='三元组谓语')
    parser.add_argument('--object', dest='object_', help='三元组宾语')
    parser.add_argument('--limit', '-l', type=int, default=10, help='返回结果数量')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--list-indexes', action='store_true', help='列出可用索引')
    parser.add_argument('--list-aliases', action='store_true', help='列出实体别名')
    
    args = parser.parse_args()
    if args.limit <= 0:
        parser.error('--limit 必须为正整数')
    
    if args.list_indexes:
        print("=== 可用索引 ===")
        for key, info in INDEXES.items():
            print(f"\n  {key}: {info['name']}")
            print(f"    文件: {info['file']}")
            print(f"    说明: {info['desc']}")
        return
    
    if args.list_aliases:
        aliases = load_aliases()
        print("=== 实体别名映射 ===")
        for standard, alias_list in aliases.get('entities', {}).items():
            print(f"\n  {standard}:")
            for alias in alias_list:
                print(f"    - {alias}")
        return
    
    kb = load_kb(args.index)
    index_info = INDEXES[args.index]
    
    if args.stats:
        from collections import Counter
        categories = [d.get('category', '未分类') for d in kb['docs']]
        stats = Counter(categories)
        print(f"=== {index_info['name']} 统计 ===")
        print(f"说明: {index_info['desc']}\n")
        for cat, count in stats.most_common():
            print(f"  {cat}: {count} 条")
        
        # 剧情库额外显示章节统计
        if args.index == 'story':
            chapters = [d.get('chapter', '未分类') for d in kb['docs']]
            ch_stats = Counter(chapters)
            print(f"\n=== 章节分布 ===")
            for ch, count in ch_stats.most_common(15):
                print(f"  {ch}: {count} 条")
        
        print(f"\n总计: {len(kb['docs'])} 条")
        return
    
    if args.smart:
        results = smart_search(kb, args.smart, args.limit)
    elif args.category:
        results = search_by_category(kb, args.category, args.limit)
    elif args.chapter:
        results = search_by_chapter(kb, args.chapter, args.limit)
    elif args.entity:
        results = search_by_entity(kb, args.entity, args.limit)
    elif args.search:
        results = search_by_keyword(kb, args.search, args.limit)
    elif args.subject or args.predicate or args.object_:
        results = search_by_triple(kb, args.subject, args.predicate, args.object_, args.limit)
    else:
        parser.print_help()
        return
    
    print(f"=== {index_info['name']} 查询结果 ===")
    print(f"找到 {len(results)} 条结果:\n")
    for doc in results:
        print(format_result(doc))

if __name__ == '__main__':
    main()
