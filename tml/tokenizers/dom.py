from __future__ import absolute_import
# -*- coding: utf-8 -*-
import re
from lxml import etree, html

from ..utils import split_sentences, hash_fetch, to_string
from ..session_vars import get_current_context
from ..config import CONFIG

__author__ = 'xepa4ep'


class DomTokenizer(object):

    text = None
    context = None
    tokens = None
    options = None

    def __init__(self, context=None, options=None):
        self.context = context
        self.options = options
        self.reset_context()

    def parseHtml(self, doc):
        document = html.fromstring(doc)
        if document.tag == 'html':
            p = document.find('body')
            return p
        return document

    def element_node(self, node):
        if self.have_childrens(node):
            return True
        return False

    def text_node(self, node):
        if not self.have_childrens(node) and node.text:
            return True
        return False

    def node_children(self, node):
        return node.getchildren()

    def have_childrens(self, node):
        childrens = self.node_children(node)
        if len(childrens) > 0:
            return True
        return False

    def node_inner_html(self, node):
        inner_html = ""
        for child in self.node_children(node):
            inner_html += etree.tostring(child)
        return inner_html

    def node_html(self, node):
        return etree.tostring(node)

    def translate(self, doc):
        html_tree = self.parseHtml(doc)
        if isinstance(html_tree, str):
            return self.translate_tml(html_tree)
        if html_tree.getparent().tag.lower() == 'body':
            html_tree = html_tree.getparent()
        return self.translate_tree(html_tree)

    def translate_tree(self, node):
        if self.text_node(node) and not self.is_inline_node(node):
            container_value = self.translate_tml(node.text)
            return self.generate_html_token(node, container_value)
        html, data_buffer = to_string(""), to_string("")
        if node.text:
            data_buffer += to_string(node.text)
        for child in node.iterchildren():
            if self.is_non_translatable_node(child):
                html += to_string(self.node_html(child))
            elif self.text_node(child) and not self.is_inline_node(child):
                container_value = self.translate_tml(child.text)
                html += to_string(self.generate_html_token(child, container_value))
            elif self.text_node(child) and self.is_inline_node(child):
                data_buffer += self.generate_tml_tags(child)
            elif self.is_separator_node(child):
                if data_buffer:
                    html += to_string(self.translate_tml(data_buffer))
                html += to_string(self.generate_html_token(child))
                data_buffer = ""
            else:
                if data_buffer:
                    html += to_string(self.translate_tml(data_buffer))
                container_value = self.translate_tree(child)
                html += to_string(self.generate_html_token(child, container_value))
                data_buffer = ""
            if child.tail:
                data_buffer += child.tail
        if data_buffer:
            html += to_string(self.translate_tml(data_buffer))
        return html


    def is_no_translate_node(self, node):
        for name, attribute in node.attrib.items():
            if name == 'notranslate' or 'notranslate' in attribute:
                return True
        return False

    def is_non_translatable_node(self, node=None):
        if self.text_node(node) and node.tag.lower() in self.option('nodes.scripts'):
            return True
        if self.is_no_translate_node(node):
            return True
        return False

    def translate_tml(self, tml):
        if self.is_empty_string(tml):
            return tml
        tml = self.generate_data_tokens(tml)
        if self.option('split_sentences'):
            sentences = split_sentences(tml)
            translation = tml
            for sentence in sentences:
                if self.option('debug'):
                    sentence_translation = self.debug_translation(sentence)
                else:
                    sentence_translation = get_current_context().tr(sentence, self.tokens, self.options)[1]
                translation = translation.replace(sentence, sentence_translation)
            self.reset_context()
            return translation
        tml = re.sub('[\n]', '', tml)
        tml = re.sub('\s\s+', ' ', tml).strip()
        if self.option('debug'):
            translation = self.debug_translation(tml)
        else:
            translation = get_current_context().tr(tml, self.tokens, self.options)[1]
        self.reset_context()
        return translation

    def is_has_child_nodes(node):
        return node.children and len(node.children) > 0

    def is_between_separators(self, node):
        return not node.getparent().text or not node.tail

    def generate_tml_tags(self, node):
        data_buffer = ""
        if self.have_childrens(node):
            for child in self.node_children(node):
                if not self.have_childrens(child) and child.text:
                    data_buffer += child.text
                else:
                    data_buffer += self.generate_tml_tags(child)
        else:
            data_buffer += node.text
        token_context = self.generate_html_token(node)
        token = self.contextualize(self.adjust_name(node), token_context)
        value = self.sanitize_value(data_buffer)
        if self.is_self_closing_node(node):
            return "{" + token + "}"
        if self.is_short_token(token, value):
            return "[" + token + ": " + value + "]"
        return "[" + token + "]" + value + '[/' + token + ']'

    def option(self, name):
        value = hash_fetch(self.options, name)
        if value:
            return value
        return CONFIG.translator_option(name)

    def debug_translation(self, translation):
        return self.option('debug_format').replace('{$0}', translation)

    def is_empty_string(self, tml):
        tml = re.sub('[\s\n\r\t]', '', tml)
        return tml == ''

    def reset_context(self):
        _tokens = {}
        _tokens.update(self.context)
        self.tokens = _tokens

    def is_short_token(self, token,value):
        return (token.lower() in self.option('nodes.short')) or len(value) < 20

    def is_only_child(self, node):
        if node.getparent().tag.lower() != "body":
            return False
        return len(list(node.getparent())) == 1

    def is_inline_node(self, node):
        return node.tag.lower() in self.option('nodes.inline') and not self.is_only_child(node)

    def is_container_node(self, node):
        return node.type == 1 and not self.inline_node(node)

    def is_self_closing_node(self, node):
        return not self.have_childrens(node) and not node.text

    def is_ignored_node(self, node):
        if not self.element_node(node):
            return True
        return node.tag.lower() in self.option('nodes.ignored')

    def is_valid_text_node(self, node):
        if not node:
            return False
        return self.text_node(node) and not self.is_empty_string(node.text)

    def is_separator_node(self, node):
        if node is not None:
            return False
        return not self.have_childrens(node) and node.tag.lower() in self.option('nodes.splitters')

    def sanitize_value(self, value):
        return re.sub('^\s+', '', value)

    def generate_data_tokens(self, text):
        #return text
        if self.option('data_tokens.special.enabled'):
            matches = re.findall(self.option('data_tokens.special.regex'), text)
            for match in matches:
                token = match[1, -1] ##must be fix ruby code
                self.context[token] = match
                text = re.sub(match, "{%(token)s}" % {"token": token}, text)
        if self.option('data_tokens.date.enabled'):
            token_name = self.option('data_tokens.date.name')
            formats = self.option('data_tokens.date.formats')
            for format_item in formats:
                regex = format_item[0]
                matches = re.findall(regex, text)

                if matches:
                    for match in matches:
                        if not match[0]:
                            continue
                        date = match[0]
                        token = self.contextualize(token_name, date)
                        replacement = "{%(token)s}" % {"token": token}
                        text = re.sub(date, replacement, text)
        rules = self.option('data_tokens.rules')
        if rules:
            for rule in rules:
                if not rule.get("enabled", False):
                    continue
                matches = re.findall(rule.get('regex'), text)
                if matches:
                    for match in matches:
                        if not match[0]:
                            continue
                        value = match[0].strip()
                        if value:
                            token = self.contextualize(rule.get('name'), re.sub('[.,;\s]', '', value))
                            text = re.sub(value, re.sub(value, "{%(token)s}" % {"token": token}, value), text)
        return text


    def generate_html_token(self, node, value=None):
        name = node.tag.lower()
        attrs = node.attrib
        attr_hash = {}
        if not value:
            value ='{$0}'
        else:
            value = value
        if len(attrs) == 0:
            if self.is_self_closing_node(node):
                if name in self.option("nodes.splitters"):
                    return "<" + name + "/>"
                return "<" + name + ">" + "</" + name + ">"
            return "<" + name + ">" + value + "</" + name + ">"

        for attr_name, attr in attrs.items():
            attr_hash[attr_name] = attr
        keys = sorted(attr_hash.items(), key=lambda x: x[0])
        attr = []
        for key in keys:
            if "'" in key[1]:
                quote = '"'
            else:
                quote = "'"
            attr.append(key[0] + '=' + quote + key[1] + quote)


        attr = " ".join(attr)
        if self.is_self_closing_node(node):
            return '<' + name + ' ' + attr + '>' + '</' + name + '>'
        return '<' + name + ' ' + attr + '>' + value + '</' + name + '>'

    def adjust_name(self, node):
        name = node.tag.lower()
        node_map = self.option('name_mapping')
        if name in node_map:
            return node_map.get(name)
        else:
            return name

    def contextualize(self, name, context):
        """
        """
        if name in self.tokens and self.tokens[name] != context:
            index = 0
            matches = re.findall('\d+$', name)
            if matches and len(matches) > 0:
                index = int(matches[len(matches) - 1])
                name = re.sub(str(index), '', name)
            name += str(index + 1)
            return self.contextualize(name, context)
        self.tokens[name] = context
        return name


    # def debug(self, doc):
    #     self.doc = doc
    #     return self.debug_tree(self.doc, 0)

    # def debug_tree(self, node, depth):
    #     tml_logger = get_logger()

    #     padding = ("=" * (depth+1))
    #     tml_logger.debug(padding + '=> ' + (node) + ': ' + self.node_info(node))

    #     for child in node.children:
    #         self.debug_tree(child, depth+1)


    # def node_info(self, node):
    #     info = []
    #     info.append(node.tag)

    #     if self.is_inline_node(node):
    #         info.append('inline')
    #         if self.has_inline_or_text_siblings(node):
    #             info.append('sentence')
    #         else:
    #             info.append('only translatable')

    #     if self.self_closing_node(node):
    #         info.append('self closing')

    #     if self.only_child(node):
    #         info.append('only child')

    #     info_text = ", ".join(info)
    #     if node.text:
    #         return "[" + info_text + "]: " + node.text
    #     else:
    #         return "[" + info_text + "]"


