#!/usr/bin/env python3
"""从完整库重建分库；只校正明确核验过的误分类，不推测剧情章节。"""
import argparse
import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
CORRECTIONS = {
    'b0427ed8b3b98ed9e1bb9ea85aa8c4df870f9bfdeadbc45fbb797b28df71e728': '界面介绍',
    '7024c2be15fe2110f123ed942705d8aafceaed7f7909adf5f9fed10d5e1d53c7': '网络功能',
}


def build_indexes(full, old_story):
    full = copy.deepcopy(full)
    chapters = {d['idx']: d.get('chapter', '未分类') for d in old_story['docs']}
    mechanic, story = [], []
    for doc in full['docs']:
        if doc['passage'].startswith('世界模式-体力\n'):
            doc['category'] = '世界模式'
        for prefix, category in CORRECTIONS.items():
            if doc['idx'].startswith(prefix):
                doc['category'] = category
        record = copy.deepcopy(doc)
        if doc['category'] == '剧情故事':
            record['chapter'] = chapters.get(doc['idx'], '未分类')
            story.append(record)
        else:
            mechanic.append(record)
    return full, mechanic, story


def render_preserving_docs(text, value):
    """保留未变记录原有排版，避免历史 JSON 格式产生全库 diff。"""
    match = re.search(r'"docs"\s*:\s*\[', text)
    decoder = json.JSONDecoder()
    pos = match.end()
    blocks = {}
    while True:
        while text[pos].isspace() or text[pos] == ',':
            pos += 1
        if text[pos] == ']':
            end = pos
            break
        record, stop = decoder.raw_decode(text, pos)
        blocks[record['idx']] = (record, text[pos:stop])
        pos = stop
    indent = ' ' * 17
    rendered = []
    for record in value['docs']:
        old, block = blocks.get(record['idx'], (None, None))
        if old == record:
            rendered.append(block)
        else:
            rendered.append(json.dumps(record, ensure_ascii=False, indent=4).replace('\n', '\n' + indent))
    return text[:match.end()] + '\n' + indent + (',\n' + indent).join(rendered) + '\n             ' + text[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='校验一致性，不写入')
    args = parser.parse_args()
    def read(name):
        return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))
    full, mechanic, story = build_indexes(read('knowledge_base.json'), read('story_kb.json'))
    outputs = {'knowledge_base.json': full}
    for name, docs in [('mechanic_kb.json', mechanic), ('story_kb.json', story)]:
        kb = read(name)
        kb['docs'] = docs
        outputs[name] = kb
    for name, value in outputs.items():
        if args.check:
            if read(name) != value:
                raise SystemExit(f'{name} 不一致，请运行 python rebuild_indexes.py')
        else:
            path = ROOT / name
            path.write_text(render_preserving_docs(path.read_text(encoding='utf-8-sig'), value), encoding='utf-8')
    print(f'校验通过：总库 {len(full["docs"])}，机制 {len(mechanic)}，剧情 {len(story)}')


if __name__ == '__main__':
    main()
