import re
import datetime
import functools
from ..session_vars import get_current_context
from .. import build_context
from ..context import LanguageContext
from ..config import CONFIG
from ..token.data import DataToken


def context_configured(fn):

    @functools.wraps(fn)
    def _context_configured(self, *args, **kwargs):
        context = get_current_context()
        if context is None:
            build_context(context=LanguageContext)
            context = get_current_context()
        return fn(self, context, *args, **kwargs)

    return _context_configured


class tmldate(datetime.date):

    @context_configured
    def translate(self, language_context, format='default', options=None):
        options = {} if options is None else options
        if format.startswith(':'):
            label = CONFIG.get_custom_date_format(format[1:])
        else:
            label = format

        selected_tokens = []
        using_tokens = '{' in label
        if using_tokens:
            selected_tokens = [token.name(dict(parens=True)) for token in DataToken.parse(label)]
        else:
            symbols = re.compile(r'(%\w)').findall(label)
            for symbol in symbols:
                token = CONFIG.strftime_symbol_to_token(symbol)
                if not token:
                    continue
                selected_tokens.append(token)
                label = label.replace(symbol, token)
        tokens = {}
        for token in selected_tokens:
            token_no_parens = token.lstrip('{').rstrip('}')
            extractor = getattr(self, '_extract_{}'.format(token_no_parens), None)
            if not extractor or not callable(extractor):
                raise Exception("Extractor for token `%s` not registered" % token)
            tokens[token_no_parens] = extractor(language_context, options)
        return language_context.tr(label, description='', data=tokens, options=options)[1]

    def _extract_days(self, language_context, options):
        if options.get('with_leading_zero', False):
            return self.strftime('%d')
        else:
            return str(self.day)

    def _extract_months(self, language_context, options):
        if options.get('with_leading_zero', False):
            return self.strftime('%m')
        else:
            return str(self.month)

    def _extract_years(self, language_context, options):
        return str(self.year)

    def exract_year_days(self, language_context, options):
        yday = self.timetuple().tm_yday
        if options.get('with_leading_zero', False):
            return '%02d' % yday
        return str(yday)

    def _extract_week_num(self, language_context, options):
        return self.isocalendar()[1]

    def _extract_week_days(self, language_context, options):
        return self.strftime('%w')

    def _extract_short_years(self, language_context, options):
        return self.strftime('%y')

    def _extract_short_week_day_name(self, language_context, options):
        return language_context.tr(CONFIG.get_abbr_day_name(self.weekday()), description='Short name for a day of a week', data={}, options=options)[1]

    def _extract_week_day_name(self, language_context, options):
        return language_context.tr(CONFIG.get_day_name(self.weekday()), description='Day of a week', data={}, options=options)[1]

    def _extract_short_month_name(self, language_context, options):
        return language_context.tr(CONFIG.get_abbr_month_name(self.month - 1), 'Short month name', data={}, options=options)[1]

    def _extract_month_name(self, language_context, options):
        return language_context.tr(CONFIG.get_month_name(self.month - 1), description='Month name', data={}, options=options)[1]

    def _extract_day_of_month(self, language_context, options):
        return self.strftime('%d')
