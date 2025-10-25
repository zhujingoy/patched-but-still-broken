import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from novel_parser import NovelParser


class TestNovelParser(unittest.TestCase):
    
    def test_parse_single_chapter(self):
        text = "第一章 开始\n这是第一章的内容。\n这是第二段。"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]['title'], '第一章 开始')
        self.assertEqual(len(chapters[0]['paragraphs']), 2)
        self.assertIn('这是第一章的内容。', chapters[0]['paragraphs'])
    
    def test_parse_multiple_chapters(self):
        text = "第一章 开始\n内容1\n第二章 继续\n内容2\n第三章 结束\n内容3"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0]['title'], '第一章 开始')
        self.assertEqual(chapters[1]['title'], '第二章 继续')
        self.assertEqual(chapters[2]['title'], '第三章 结束')
    
    def test_parse_chapter_with_numeric(self):
        text = "第1章 测试\n内容"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]['title'], '第1章 测试')
    
    def test_parse_chapter_with_hui(self):
        text = "第一回 古代\n内容"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]['title'], '第一回 古代')
    
    def test_parse_chapter_with_jie(self):
        text = "第001节 科技\n内容"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]['title'], '第001节 科技')
    
    def test_parse_no_chapter_markers(self):
        text = "这是一段没有章节标记的文本。\n这是第二段。"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertEqual(chapters[0]['title'], '全文')
        self.assertEqual(len(chapters[0]['paragraphs']), 2)
    
    def test_parse_empty_text(self):
        text = ""
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 0)
    
    def test_parse_whitespace_only(self):
        text = "   \n\n   \n"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 0)
    
    def test_get_chapter_valid_index(self):
        text = "第一章 开始\n内容1\n第二章 继续\n内容2"
        parser = NovelParser(text)
        parser.parse()
        
        chapter = parser.get_chapter(0)
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter['title'], '第一章 开始')
        
        chapter = parser.get_chapter(1)
        self.assertIsNotNone(chapter)
        self.assertEqual(chapter['title'], '第二章 继续')
    
    def test_get_chapter_invalid_index(self):
        text = "第一章 开始\n内容"
        parser = NovelParser(text)
        parser.parse()
        
        self.assertIsNone(parser.get_chapter(-1))
        self.assertIsNone(parser.get_chapter(10))
    
    def test_get_chapter_boundary_index(self):
        text = "第一章 开始\n内容1\n第二章 继续\n内容2"
        parser = NovelParser(text)
        parser.parse()
        
        self.assertIsNotNone(parser.get_chapter(0))
        self.assertIsNotNone(parser.get_chapter(1))
        self.assertIsNone(parser.get_chapter(2))
    
    def test_get_total_chapters(self):
        text = "第一章 开始\n内容1\n第二章 继续\n内容2\n第三章 结束\n内容3"
        parser = NovelParser(text)
        parser.parse()
        
        self.assertEqual(parser.get_total_chapters(), 3)
    
    def test_get_total_chapters_empty(self):
        text = ""
        parser = NovelParser(text)
        parser.parse()
        
        self.assertEqual(parser.get_total_chapters(), 0)
    
    def test_parse_chapter_with_empty_paragraphs(self):
        text = "第一章 开始\n内容1\n\n\n内容2\n\n"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters[0]['paragraphs']), 2)
        self.assertEqual(chapters[0]['paragraphs'][0], '内容1')
        self.assertEqual(chapters[0]['paragraphs'][1], '内容2')
    
    def test_parse_consecutive_chapters(self):
        text = "第一章 A\n内容A\n第二章 B\n第三章 C\n内容C"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 2)
        self.assertEqual(chapters[0]['title'], '第一章 A')
        self.assertEqual(chapters[1]['title'], '第二章 B')
    
    def test_parse_long_chapter_title(self):
        text = "第一章 这是一个很长很长的章节标题，包含了很多信息\n内容"
        parser = NovelParser(text)
        chapters = parser.parse()
        
        self.assertEqual(len(chapters), 1)
        self.assertIn('很长很长的章节标题', chapters[0]['title'])


if __name__ == '__main__':
    unittest.main()
