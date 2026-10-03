import contextlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

import query
from rebuild_indexes import ROOT, build_indexes


def doc(idx, passage='', entities=(), triples=()):
    return dict(idx=idx, passage=passage, extracted_entities=list(entities), extracted_triples=list(triples))


class QueryTests(unittest.TestCase):
    def test_import_does_not_replace_stdout(self):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            importlib.reload(query)
            self.assertIs(sys.stdout, stream)

    def test_entity_alias_and_exact_match(self):
        kb = {'docs': [doc('arc', entities=['音弧']), doc('other', entities=['音弧判定'])]}
        self.assertEqual([d['idx'] for d in query.search_by_entity(kb, '蛇')], ['arc'])

    def test_relation_alias(self):
        kb = {'docs': [doc('arc', triples=[['音弧', '俗称', '蛇']])]}
        self.assertEqual(len(query.search_by_triple(kb, subject='arc', predicate='简称')), 1)

    def test_smart_search_ranks_entire_index(self):
        kb = {'docs': [doc(str(i), '这里有光') for i in range(40)] + [doc('best', '光', ['光'])]}
        self.assertEqual(query.smart_search(kb, '光', 10)[0]['idx'], 'best')

    def test_empty_and_nonpositive_queries(self):
        kb = {'docs': [doc('one', '光', ['光'])]}
        for fn in (query.search_by_keyword, query.search_by_entity, query.search_by_chapter,
                   query.search_by_category, query.smart_search):
            self.assertEqual(fn(kb, '', 10), [])
            self.assertEqual(fn(kb, '光', 0), [])
            self.assertEqual(fn(kb, '光', -1), [])
        self.assertEqual(query.search_by_triple(kb), [])

    def test_cli_outside_repo(self):
        result = subprocess.run([sys.executable, str(ROOT / 'query.py'), '--entity', 'ptt'],
                                cwd=ROOT.parent, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('潜力值', result.stdout)

    def test_cli_rejects_nonpositive_limit(self):
        result = subprocess.run([sys.executable, str(ROOT / 'query.py'), '--limit', '0'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.full = query.load_kb('all')
        cls.mechanic = query.load_kb('mechanic')
        cls.story = query.load_kb('story')

    def test_schema_and_unique_ids(self):
        for kb in (self.full, self.mechanic, self.story):
            ids = [d['idx'] for d in kb['docs']]
            self.assertEqual(len(ids), len(set(ids)))
            for d in kb['docs']:
                self.assertRegex(d['idx'], r'^[0-9a-f]{64}$')
                self.assertIsInstance(d['passage'], str)
                self.assertTrue(d['passage'].strip())
                self.assertIsInstance(d['category'], str)
                self.assertTrue(all(isinstance(e, str) for e in d['extracted_entities']))
                self.assertTrue(all(len(t) == 3 and all(isinstance(x, str) for x in t)
                                    for t in d['extracted_triples']))

    def test_partition_and_content_equality(self):
        full = {d['idx']: d for d in self.full['docs']}
        mechanic = {d['idx']: d for d in self.mechanic['docs']}
        story = {d['idx']: {k: v for k, v in d.items() if k != 'chapter'} for d in self.story['docs']}
        self.assertFalse(mechanic.keys() & story.keys())
        self.assertEqual(full, mechanic | story)
        self.assertEqual(len(full), 2972)
        self.assertTrue(all(d['category'] != '剧情故事' for d in mechanic.values()))
        self.assertTrue(all(d['category'] == '剧情故事' for d in story.values()))

    def test_rebuild_is_idempotent(self):
        full, mechanic, story = build_indexes(self.full, self.story)
        self.assertEqual(full, self.full)
        self.assertEqual(mechanic, self.mechanic['docs'])
        self.assertEqual(story, self.story['docs'])

    def test_corrected_mechanics(self):
        for title in ('回忆收集条', '好友（关注）系统', '世界模式-体力'):
            self.assertTrue(any(d['passage'].startswith(title + '\n') for d in self.mechanic['docs']))
            self.assertFalse(any(d['passage'].startswith(title + '\n') for d in self.story['docs']))

    def test_documented_examples(self):
        self.assertTrue(query.search_by_chapter(self.story, '主线-第1章'))
        for alias in ('蛇', 'ptt', 'ETR'):
            self.assertTrue(query.search_by_entity(self.mechanic, alias))


if __name__ == '__main__':
    unittest.main()
