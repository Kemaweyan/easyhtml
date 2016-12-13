import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from easyhtml import dom

class TestPlainText(unittest.TestCase):

    def test_create_plain_text_without_spaces(self):
        text = dom.PlainText('test')
        self.assertEqual(text.data, 'test')
        self.assertEqual(text._raw_html, 'test')

    def test_create_plain_text_with_single_spaces(self):
        text = dom.PlainText(' test ')
        self.assertEqual(text.data, ' test ')
        self.assertEqual(text._raw_html, ' test ')

    def test_create_plain_text_with_multiple_spaces(self):
        text = dom.PlainText('   test   ')
        self.assertEqual(text.data, ' test ')
        self.assertEqual(text._raw_html, '   test   ')

    def test_create_plain_text_with_other_space_symbols(self):
        text = dom.PlainText('\t test\t')
        self.assertEqual(text.data, ' test ')
        self.assertEqual(text._raw_html, '\t test\t')

    def test_plain_text_to_string_with_other_space_symbols(self):
        text = dom.PlainText('\t test\t')
        self.assertEqual(str(text), ' test ')

    def test_plain_text_raw_html_with_other_space_symbols(self):
        text = dom.PlainText('\t test\t')
        self.assertEqual(text.raw_html, '\t test\t')




class TestNamedEntity(unittest.TestCase):

    def test_create_named_entity_valid(self):
        text = dom.NamedEntity('lt')
        self.assertEqual(text.data, '<')
        self.assertEqual(text._raw_html, '&lt;')

    def test_create_named_entity_invalid(self):
        with self.assertRaises(KeyError):
            dom.NamedEntity('test')

    def test_named_entity_to_string(self):
        text = dom.NamedEntity('lt')
        self.assertEqual(str(text), '<')

    def test_named_entity_raw_html(self):
        text = dom.NamedEntity('lt')
        self.assertEqual(text.raw_html, '&lt;')




class TestNumEntity(unittest.TestCase):

    def test_create_num_entity_dec(self):
        text = dom.NumEntity('60')
        self.assertEqual(text.data, '<')
        self.assertEqual(text._raw_html, '&#60;')

    def test_create_num_entity_hex(self):
        text = dom.NumEntity('x3c')
        self.assertEqual(text.data, '<')
        self.assertEqual(text._raw_html, '&#x3c;')

    def test_create_num_entity_invalid(self):
        with self.assertRaises(ValueError):
            dom.NumEntity('test')

    def test_num_entity_to_string(self):
        text = dom.NumEntity('60')
        self.assertEqual(str(text), '<')

    def test_num_entity_raw_html(self):
        text = dom.NumEntity('60')
        self.assertEqual(text.raw_html, '&#60;')




class TestHTMLComment(unittest.TestCase):

    def test_create_comment(self):
        text = dom.HTMLComment('test')
        self.assertEqual(text.data, '')
        self.assertEqual(text._raw_html, '<!-- test -->')

    def test_comment_to_string(self):
        text = dom.HTMLComment('test')
        self.assertEqual(str(text), '')

    def test_comment_raw_html(self):
        text = dom.HTMLComment('test')
        self.assertEqual(text.raw_html, '<!-- test -->\n')




class TestDoctypeDeclaration(unittest.TestCase):

    def test_create_DoctypeDeclaration(self):
        text = dom.DoctypeDeclaration('test')
        self.assertEqual(text.data, '')
        self.assertEqual(text._raw_html, '<!test>')

    def test_DoctypeDeclaration_to_string(self):
        text = dom.DoctypeDeclaration('test')
        self.assertEqual(str(text), '')

    def test_DoctypeDeclaration_raw_html(self):
        text = dom.DoctypeDeclaration('test')
        self.assertEqual(text.raw_html, '<!test>\n')




class TestTextNode(unittest.TestCase):

    def setUp(self):
        self.tn = dom.TextNode()

    def test_text_node_append_element(self):
        e = Mock()
        self.tn.append(e)
        self.assertIn(e, self.tn.elements)

    def test_text_node_to_str(self):
        e1 = MagicMock()
        e2 = MagicMock()
        e1.__str__.return_value = 'test1\n'
        e2.__str__.return_value = 'test2\n'
        self.tn.append(e1)
        self.tn.append(e2)
        self.assertEqual(str(self.tn), 'test1\ntest2\n')

    def test_text_node_raw_html_with_newline(self):
        e1 = Mock()
        e2 = Mock()
        e1.raw_html = 'test1\n'
        e2.raw_html = 'test2\n'
        self.tn.append(e1)
        self.tn.append(e2)
        self.assertEqual(self.tn.raw_html, 'test1\ntest2\n')

    def test_text_node_raw_html_without_newline(self):
        e1 = Mock()
        e2 = Mock()
        e1.raw_html = 'test1\n'
        e2.raw_html = 'test2'
        self.tn.append(e1)
        self.tn.append(e2)
        self.assertEqual(self.tn.raw_html, 'test1\ntest2\n')




class TestHTMLDocument(unittest.TestCase):

    def setUp(self):
        self.doc = dom.HTMLDocument()

    def test_is_single(self):
        self.assertFalse(self.doc.single)

    def test_raw_html_property(self):
        foo = Mock(raw_html='foo\n')
        bar = Mock(raw_html='bar\n')
        self.doc.doctype = Mock(raw_html='<!doctype>\n')
        self.doc.elements = [foo, bar]
        self.assertEqual(self.doc.raw_html, '<!doctype>\nfoo\nbar\n')

    def test_inner_html_property(self):
        foo = Mock(raw_html='foo\n')
        bar = Mock(raw_html='bar\n')
        self.doc.elements = [foo, bar]
        self.assertEqual(self.doc.inner_html, 'foo\nbar\n')

    def test_tags_property_found(self):
        foo = Mock(spec=dom.HTMLTag)
        self.doc.elements = [foo]
        tags = list(self.doc.tags)
        self.assertIn(foo, tags)

    def test_tags_property_not_found(self):
        foo = Mock(spec=dom.TextNode)
        self.doc.elements = [foo]
        tags = list(self.doc.tags)
        self.assertNotIn(foo, tags)

    def test_get_tags_found(self):
        foo = MagicMock(spec=dom.HTMLTag)
        self.doc.elements = [foo]
        tags = list(self.doc.get_all_tags())
        self.assertIn(foo, tags)

    def test_get_tags_not_found(self):
        foo = MagicMock(spec=dom.TextNode)
        self.doc.elements = [foo]
        tags = list(self.doc.get_all_tags())
        self.assertNotIn(foo, tags)

    def test_get_tags_nested_found(self):
        foo = MagicMock(spec=dom.HTMLTag)
        bar = MagicMock(spec=dom.HTMLTag)
        foo.get_all_tags.return_value = [bar]
        self.doc.elements = [foo]
        tags = list(self.doc.get_all_tags())
        self.assertIn(foo, tags)
        self.assertIn(bar, tags)

    def test_get_tags_nested_not_found(self):
        foo = MagicMock(spec=dom.HTMLTag)
        bar = MagicMock(spec=dom.TextNode)
        foo.get_all_tags.return_value = []
        self.doc.elements = [foo]
        tags = list(self.doc.get_all_tags())
        self.assertIn(foo, tags)
        self.assertNotIn(bar, tags)

    def test_append_element(self):
        e = Mock()
        self.doc.append(e)
        self.assertIn(e, self.doc.elements)

    def test_append_text_node_existing(self):
        text_node = Mock(spec=dom.TextNode)
        self.doc.elements.append(text_node)
        e = Mock(spec=dom.HTMLText)
        self.doc.append(e)
        text_node.append.assert_called_with(e)

    @patch('easyhtml.dom.TextNode')
    def test_append_text_node_empty_list(self, text_node_mock):
        e = Mock(spec=dom.HTMLText)
        self.doc.append(e)
        text_node_mock.assert_called_with()
        text_node_mock.return_value.append.assert_called_with(e)

    @patch.object(dom.TextNode, 'append')
    @patch.object(dom.TextNode, '__init__', return_value=None)
    def test_append_text_node_non_text_node(self, init_mock, append_mock):
        self.doc.elements.append('test')
        e = Mock(spec=dom.HTMLText)
        self.doc.append(e)
        init_mock.assert_called_with()
        append_mock.assert_called_with(e)

    def test_get_tags_by_name(self):
        tag1 = Mock(tag_name='div')
        tag2 = Mock(tag_name='div')
        tag3 = Mock(tag_name='p')
        self.doc.get_all_tags = Mock(return_value=[tag1, tag2, tag3])
        tags = list(self.doc.get_tags_by_name('div'))
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertNotIn(tag3, tags)

    def test_get_children(self):
        tag1 = Mock()
        tag1.check_attrs.return_value = True
        tag2 = Mock()
        tag2.check_attrs.return_value = True
        tag3 = Mock()
        tag3.check_attrs.return_value = False
        self.doc.get_all_tags = Mock(return_value=[tag1, tag2, tag3])
        tags = list(self.doc.get_children('test'))
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertNotIn(tag3, tags)
        tag1.check_attrs.assert_called_with('test')
        tag2.check_attrs.assert_called_with('test')
        tag3.check_attrs.assert_called_with('test')

    def test_get_element_by_id_ok(self):
        tag1 = Mock()
        tag1.check_attr.return_value = True
        tag2 = Mock()
        tag2.check_attr.return_value = False
        self.doc.get_all_tags = Mock(return_value=[tag1, tag2])
        self.assertEqual(self.doc.get_element_by_id('test'), tag1)
        tag1.check_attr.assert_called_with('id', 'test')

    def test_get_element_by_id_none(self):
        tag1 = Mock()
        tag1.check_attr.return_value = False
        tag2 = Mock()
        tag2.check_attr.return_value = False
        self.doc.get_all_tags = Mock(return_value=[tag1, tag2])
        self.assertIsNone(self.doc.get_element_by_id('test'))
        tag1.check_attr.assert_called_with('id', 'test')
        tag2.check_attr.assert_called_with('id', 'test')



class TestHTMLTag(unittest.TestCase):

    def test_create_tag(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1'), ('attr2', 'value2')])
        self.assertEqual(tag.tag_name, 'tag')
        self.assertEqual(tag.attrs['attr1'], 'value1')
        self.assertEqual(tag.attrs['attr2'], 'value2')

    def test_single_yes(self):
        tag = dom.HTMLTag('tag', [])
        tag.single_tags = ('tag')
        self.assertTrue(tag.single)

    def test_single_no(self):
        tag = dom.HTMLTag('tag', [])
        tag.single_tags = tuple()
        self.assertFalse(tag.single)

    def test_start_tag(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertEqual(tag.start_tag, '<tag attr1="value1">\n')

    def test_end_tag(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertEqual(tag.end_tag, '</tag>\n')

    @patch.object(dom.HTMLTag, 'inner_html', return_value='test\n', new_callable=PropertyMock)
    @patch.object(dom.HTMLTag, 'single', return_value=False, new_callable=PropertyMock)
    def test_raw_html_non_single(self, single_mock, inner_html_mock):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertEqual(tag.raw_html, '<tag attr1="value1">\n    test\n</tag>\n')

    @patch.object(dom.HTMLTag, 'single', return_value=True, new_callable=PropertyMock)
    def test_raw_html_single(self, single_mock):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertEqual(tag.raw_html, '<tag attr1="value1">\n')

    def test_get_attr_existing(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertEqual(tag.get_attr('attr1'), 'value1')

    def test_get_attr_none(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertIsNone(tag.get_attr('attr2'))

    def test_check_attr_correct(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertTrue(tag.check_attr('attr1', 'value1'))

    def test_check_attr_wrong(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertFalse(tag.check_attr('attr1', 'value2'))

    def test_check_attr_not_exists(self):
        tag = dom.HTMLTag('tag', [('attr1', 'value1')])
        self.assertFalse(tag.check_attr('attr2', 'value2'))

    def test_check_attr_class_single_correct(self):
        tag = dom.HTMLTag('tag', [('class', 'foo')])
        self.assertTrue(tag.check_attr('class', 'foo'))

    def test_check_attr_class_single_wrong(self):
        tag = dom.HTMLTag('tag', [('class', 'foo')])
        self.assertFalse(tag.check_attr('class', 'bar'))

    def test_check_attr_class_not_specified(self):
        tag = dom.HTMLTag('tag', [])
        self.assertFalse(tag.check_attr('class', 'foo'))

    def test_check_attr_class_multiple_correct(self):
        tag = dom.HTMLTag('tag', [('class', 'foo baz')])
        self.assertTrue(tag.check_attr('class', 'foo'))

    def test_check_attr_class_multiple_wrong(self):
        tag = dom.HTMLTag('tag', [('class', 'foo baz')])
        self.assertFalse(tag.check_attr('class', 'bar'))

    def test_check_attrs_correct(self):
        tag = dom.HTMLTag('tag', [])
        tag.check_attr = Mock(return_value=True)
        self.assertTrue(tag.check_attrs('attr1=value1; attr2=value2'))
        tag.check_attr.any_call('attr1', 'value1')
        tag.check_attr.any_call('attr2', 'value2')

    def test_check_attrs_wrong(self):
        tag = dom.HTMLTag('tag', [])
        tag.check_attr = Mock(return_value=False)
        self.assertFalse(tag.check_attrs('attr1=value1; attr2=value2'))
        tag.check_attr.any_call('attr1', 'value1')
        tag.check_attr.any_call('attr2', 'value2')

    def test_check_attrs_one_wrong(self):
        tag = dom.HTMLTag('tag', [])
        tag.check_attr = Mock(side_effect=[True, False])
        self.assertFalse(tag.check_attrs('attr1=value1; attr2=value1'))
        tag.check_attr.any_call('attr1', 'value1')
        tag.check_attr.any_call('attr2', 'value2')

    def test_filter_tags_by_attrs_correct(self):
        tag = dom.HTMLTag('tag', [])
        tag.check_attrs = Mock(return_value=True)
        self.assertEqual(tag.filter_tags_by_attrs('attr1=value1; attr2=value2'), tag)
        tag.check_attrs.assert_called_with('attr1=value1; attr2=value2')

    def test_filter_tags_by_attrs_wrong(self):
        tag = dom.HTMLTag('tag', [])
        tag.check_attrs = Mock(return_value=False)
        self.assertIsNone(tag.filter_tags_by_attrs('attr1=value1; attr2=value2'))
        tag.check_attrs.assert_called_with('attr1=value1; attr2=value2')




class TestHTMLCollection(unittest.TestCase):

    def setUp(self):
        self.div = dom.HTMLTag('div', [])
        self.div_child = dom.HTMLTag('div', [])
        self.p_child = dom.HTMLTag('p', [])
        self.div_child_child = dom.HTMLTag('div', [])
        self.p_child_child = dom.HTMLTag('p', [])
        self.div_child.append(self.div_child_child)
        self.div_child.append(self.p_child_child)
        self.div.append(self.div_child)
        self.div.append(self.p_child)
        self.coll = dom.HTMLCollection((self.div,))

    def test_create_collection(self):
        coll = dom.HTMLCollection(('foo', 'bar', 'baz'))
        self.assertIn('foo', coll.elements)
        self.assertIn('bar', coll.elements)
        self.assertIn('baz', coll.elements)

    def test_iteration(self):
        coll = dom.HTMLCollection(('foo', 'bar', 'baz'))
        it = iter(coll)
        self.assertEqual(next(it), 'foo')
        self.assertEqual(next(it), 'bar')
        self.assertEqual(next(it), 'baz')

    def test_len(self):
        coll = dom.HTMLCollection(('foo', 'bar', 'baz'))
        self.assertEqual(len(coll), 3)

    def test_get_collection(self):
        foo = Mock()
        foo.return_value = dom.HTMLCollection([foo])
        bar = Mock()
        bar.return_value = dom.HTMLCollection([])
        coll = dom.HTMLCollection((foo, bar))
        result = coll._get_collection(lambda e: e())
        self.assertIn(foo, result[0].elements)
        self.assertNotIn(bar, result[1].elements)

    def test_get_tags_by_name_found(self):
        result = self.coll.get_tags_by_name('div')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)

    def test_get_tags_by_name_not_found(self):
        result = self.coll.get_tags_by_name('div')
        self.assertNotIn(self.div, result[0].elements)
        self.assertNotIn(self.p_child, result[0].elements)

    def test_get_tags_by_name_nested_child(self):
        result = self.coll.get_tags_by_name('div')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)
        self.assertIn(self.div_child_child, result[0].elements)

    def test_get_tags_by_name_nested_child_not_found(self):
        result = self.coll.get_tags_by_name('div')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)
        self.assertNotIn(self.p_child_child, result[0].elements)

    def test_get_tags_by_name_found_in_nested_collection(self):
        self.coll = dom.HTMLCollection((dom.HTMLCollection((self.div,)),))
        result = self.coll.get_tags_by_name('div')
        self.assertNotIn(self.div, result[0][0].elements)
        self.assertIn(self.div_child, result[0][0].elements)

    def test_get_children_found(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)

    def test_get_children_not_found(self):
        self.div.attrs['class'] = 'test'
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertNotIn(self.div_child, result[0].elements)

    def test_get_children_nested_child(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        self.div_child_child.attrs['class'] = 'test'
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)
        self.assertIn(self.div_child_child, result[0].elements)

    def test_get_children_nested_child_not_found(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertIn(self.div_child, result[0].elements)
        self.assertNotIn(self.div_child_child, result[0].elements)

    def test_get_children_nested_child_found_in_not_matching_parent(self):
        self.div.attrs['class'] = 'test'
        self.div_child_child.attrs['class'] = 'test'
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertNotIn(self.div_child, result[0].elements)
        self.assertIn(self.div_child_child, result[0].elements)

    def test_get_children_found_in_nested_collection(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        self.coll = dom.HTMLCollection((dom.HTMLCollection((self.div,)),))
        result = self.coll.get_children('class=test')
        self.assertNotIn(self.div, result[0][0].elements)
        self.assertIn(self.div_child, result[0][0].elements)

    def test_filter_tags_by_attrs_found(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        result = self.coll.filter_tags_by_attrs('class=test')
        self.assertIn(self.div, result.elements)
        self.assertNotIn(self.div_child, result.elements)

    def test_filter_tags_by_attrs_not_found(self):
        self.div_child.attrs['class'] = 'test'
        result = self.coll.filter_tags_by_attrs('class=test')
        self.assertNotIn(self.div, result.elements)
        self.assertNotIn(self.div_child, result.elements)

    def test_filter_tags_by_attrs_in_nested_collection_found(self):
        self.div.attrs['class'] = 'test'
        self.div_child.attrs['class'] = 'test'
        self.coll = dom.HTMLCollection((dom.HTMLCollection((self.div,)),))
        result = self.coll.filter_tags_by_attrs('class=test')
        self.assertIn(self.div, result[0].elements)
        self.assertNotIn(self.div_child, result[0].elements)

    def test_filter_tags_by_attrs_in_nested_collection_not_found(self):
        self.div_child.attrs['class'] = 'test'
        self.coll = dom.HTMLCollection((dom.HTMLCollection((self.div,)),))
        result = self.coll.filter_tags_by_attrs('class=test')
        self.assertNotIn(self.div, result[0].elements)
        self.assertNotIn(self.div_child, result[0].elements)

    def test_get_element_by_id_found(self):
        self.div.attrs['id'] = 'test'
        self.assertEqual(self.div, self.coll.get_element_by_id('test'))

    def test_get_element_by_id_not_found(self):
        self.assertIsNone(self.coll.get_element_by_id('test'))

    def test_get_element_by_id_nested_found(self):
        self.div_child.attrs['id'] = 'test'
        self.assertEqual(self.div_child, self.coll.get_element_by_id('test'))

    def test_get_element_by_id_in_nested_collection(self):
        self.div.attrs['id'] = 'test'
        self.coll = dom.HTMLCollection((dom.HTMLCollection((self.div,)),))
        self.assertEqual(self.div, self.coll.get_element_by_id('test'))
