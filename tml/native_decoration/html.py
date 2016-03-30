from __future__ import absolute_import
# encoding: UTF-8
import six
import cgi
import base64
import json
from .base import BaseDecorator

class Html(BaseDecorator):

    def decorate(self, translated_value, translation_language, original_language, translation_key, options=None):
        options = {} if options is None else options
        if not self.enabled(options):
            return translated_value
        if self.application.feature_enabled('lock_original_content') and original_language == translation_language:
            return translated_value
        classes = set(['tml_translatable'])
        if options.get('locked', False):
            classes.add('tml_locked')
        elif translation_key.language == original_language:
            if options.get('pending', False):
                classes.add('tml_pending')
            else:
                classes.add('tml_not_translated')
        elif translation_language == translation_key.language:
            classes.add('tml_translated')
        else:
            classes.add('tml_fallback')
        element = self.decoration_element('tml:label', options)
        context = {
            'element': element,
            'class_name': " ".join(classes),
            'key': translation_key.key,
            'locale': translation_language.locale,
            'text': translated_value}
        return six.u('<%(element)s class="%(class_name)s" data-translation_key="%(key)s" data-target_locale="%(locale)s">%(text)s</%(element)s>') % context

    def decorate_language_case(self, language_case, case_rule, original_value, transformed_value, options=None):
        options = {} if options is None else options
        if not self.enabled(options):
            return transformed_value
        # todo: inject properties
        data = {
            # 'keyword'       : language_case.keyword,
            # 'language_name' : language_case.language.english_name,
            # 'latin_name'    : language_case.latin_name,
            # 'native_name'   : language_case.native_name,
            'conditions'    : case_rule[0],
            'operations'    : case_rule[1],
            'original'      : original_value,
            'transformed'   : transformed_value}
        attrs = []
        attrs_dict = {
            'class'       : 'tml_language_case',
            #'data-locale' : language_case.language.locale,
            'data-rule'   : cgi.escape(base64.b64encode(json.dumps(data)).replace("\n", ''))}
        for value in attrs_dict:
            attrs.append('%(key)s="%(value)s"' % {
                'key': value,
                'value': str(attrs_dict[value])
            })
        element = self.decoration_element('tml:case', options)
        context = {
            'element': element,
            'attrs': " ".join(attrs),
            'transformed': transformed_value}
        return six.u('<%(element)s %(attrs)s>%(transformed)s</%(element)s>') % context

    def decorate_token(self, token, value, options = {}):
        if not self.enabled(options):
            return value
        element = self.decoration_element('tml:token', options)
        classes = set(['tml_token', 'tml_token_%(token)s' % {'token': token.system_name}])
        context = {
            'element': element,
            'token_name': token.name(),
            'text': value,
            'context_keys': ','.join(token.context_keys),
            'case_keys': ','.join(token.case_keys),
            'classes' : ' '.join(classes)
        }
        html = six.u("""
            <%(element)s class='%(classes)s' data-name='%(token_name)s'
            data-context='%(context_keys)s'
            data-case='%(case_keys)s'>
                %(text)s
            </%(element)s>
        """) % context
        return html

    def decorate_element(self, value, options = {}):
        if not self.enabled(options):
            return value
        element = self.decoration_element('tml:element', options)
        context = {
            'text': value,
            'element':element}
        return six.u('<%(element)s>%(text)s</%(element)s>') % context
