import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from easyhtml import parser, dom

class TestTagStack(unittest.TestCase):

    def setUp(self):
        self.stack = parser.TagStack()

    def test_create_stack(self):
        self.assertEqual(len(self.stack.tags), 0)
        self.assertIsNone(self.stack.current)

    def test_push_single_tag(self):
        tag = Mock(single=True)
        self.stack.push(tag)
        self.assertEqual(len(self.stack.tags), 0)
        self.assertIsNone(self.stack.current)

    def test_push_non_single_tag(self):
        tag = Mock(single=False)
        self.stack.push(tag)
        self.assertEqual(len(self.stack.tags), 1)
        self.assertEqual(self.stack.tags[-1], tag)
        self.assertEqual(self.stack.current, tag)

    def test_push_non_single_tag_in_non_empty_stack(self):
        self.stack.push(Mock(single=False))
        tag = Mock(single=False)
        self.stack.push(tag)
        self.assertEqual(len(self.stack.tags), 2)
        self.assertEqual(self.stack.tags[-1], tag)
        self.assertEqual(self.stack.current, tag)

    def test_pop_empty_stack(self):
        with self.assertRaises(IndexError):
            self.stack.pop()

    def test_pop_last_tag(self):
        tag = Mock(single=False)
        self.stack.push(tag)
        self.stack.pop()
        self.assertEqual(len(self.stack.tags), 0)
        self.assertIsNone(self.stack.current)

    def test_pop_non_last_tag(self):
        tag = Mock(single=False)
        self.stack.push(tag)
        self.stack.push(Mock(single=False))
        self.stack.pop()
        self.assertEqual(len(self.stack.tags), 1)
        self.assertEqual(self.stack.current, tag)

    def test_clear_stack(self):
        self.stack.push(Mock(single=False))
        self.stack.push(Mock(single=False))
        self.stack.clear()
        self.assertEqual(len(self.stack.tags), 0)
        self.assertIsNone(self.stack.current)

    def test_contains_contain(self):
        self.stack.push(Mock(single=False))
        tag = Mock(single=False, tag_name='test')
        self.stack.push(tag)
        self.assertIn('test', self.stack)

    def test_contains_not_contain(self):
        self.stack.push(Mock(single=False))
        self.assertNotIn('test', self.stack)

    def test_contains_empty(self):
        self.assertNotIn('test', self.stack)

    def test_contains_root(self):
        self.stack.push(Mock(single=False, tag_name='test'))
        self.assertNotIn('test', self.stack)

    def test_get_root_ok(self):
        tag = Mock(single=False)
        self.stack.push(tag)
        self.stack.push(Mock(single=False))
        self.assertEqual(tag, self.stack.root)

    def test_get_root_empty(self):
        with self.assertRaises(IndexError):
            root = self.stack.root




class TestParser(unittest.TestCase):

    @patch('easyhtml.parser.TagStack')
    @patch('easyhtml.dom.HTMLDocument')
    def setUp(self, document_mock, stack_mock):
        self.parser = parser.DOMParser()
        self.stack = stack_mock.return_value
        self.doc = document_mock.return_value

    def test_create_parser(self):
        self.stack.push.assert_called_with(self.doc)

    @patch('easyhtml.dom.HTMLTag')
    def test_handle_starttag(self, tag_mock):
        self.parser.handle_starttag('test', [('attr', 'value')])
        tag_mock.assert_called_with('test', [('attr', 'value')])
        self.stack.current.append.assert_called_with(tag_mock.return_value)
        self.stack.push.assert_called_with(tag_mock.return_value)

    def test_handle_endtag_empty_stack(self):
        self.stack.__contains__.return_value = False
        self.parser.handle_endtag('test')
        self.assertFalse(self.stack.pop.called)

    def test_handle_endtag_last_tag_in_the_stack(self):
        self.stack.__contains__.return_value = True
        self.stack.current.tag_name = 'test'
        self.parser.handle_endtag('test')
        self.assertEqual(self.stack.pop.call_count, 1)

    def test_handle_endtag_not_last_tag_in_the_stack(self):
        self.stack.__contains__.return_value = True
        type(self.stack.current).tag_name = PropertyMock(side_effect=['', 'test'])
        self.parser.handle_endtag('test')
        self.assertEqual(self.stack.pop.call_count, 2)

    @patch('easyhtml.dom.PlainText')
    def test_handle_data_ok(self, text_mock):
        self.parser.handle_data('test')
        text_mock.assert_called_with('test')
        self.stack.current.append.assert_called_with(text_mock.return_value)

    @patch('easyhtml.dom.PlainText')
    def test_handle_data_stripped(self, text_mock):
        self.parser.handle_data('\t \xA0')
        self.assertFalse(text_mock.called)
        self.assertFalse(self.stack.current.append.called)

    @patch('easyhtml.dom.NamedEntity')
    def test_handle_entityref_ok(self, ent_mock):
        self.parser.handle_entityref('test')
        ent_mock.assert_called_with('test')
        self.stack.current.append.assert_called_with(ent_mock.return_value)

    @patch('easyhtml.dom.PlainText')
    @patch('easyhtml.dom.NamedEntity', side_effect=KeyError)
    def test_handle_entityref_error(self, ent_mock, text_mock):
        self.parser.handle_entityref('test')
        ent_mock.assert_called_with('test')
        text_mock.assert_called_with('&test;')
        self.stack.current.append.assert_called_with(text_mock.return_value)

    @patch('easyhtml.dom.NumEntity')
    def test_handle_charref_ok(self, ent_mock):
        self.parser.handle_charref('test')
        ent_mock.assert_called_with('test')
        self.stack.current.append.assert_called_with(ent_mock.return_value)

    @patch('easyhtml.dom.PlainText')
    @patch('easyhtml.dom.NumEntity', side_effect=ValueError)
    def test_handle_charref_error(self, ent_mock, text_mock):
        self.parser.handle_charref('test')
        ent_mock.assert_called_with('test')
        text_mock.assert_called_with('&#test;')
        self.stack.current.append.assert_called_with(text_mock.return_value)

    @patch('easyhtml.dom.HTMLComment')
    def test_handle_comment_ok(self, comm_mock):
        self.parser.handle_comment('test')
        comm_mock.assert_called_with('test')
        self.stack.current.append.assert_called_with(comm_mock.return_value)

    @patch('easyhtml.dom.DoctypeDeclaration')
    def test_handle_comment_ok(self, decl_mock):
        self.parser.handle_decl('test')
        decl_mock.assert_called_with('test')
        self.assertEqual(self.stack.root.doctype, decl_mock.return_value)

    @patch('easyhtml.dom.HTMLDocument')
    def test_get_dom_ok(self, document_mock):
        dom = self.parser.get_dom()
        self.assertEqual(dom, self.stack.root)
        self.stack.clear.assert_called_with()
        document_mock.assert_called_with()
        self.stack.push.assert_called_with(document_mock.return_value)
