# encoding: UTF-8
enabled = False
save = False

def turn_on():
    """ Turn on inline tranlations """
    global enabled
    enabled = True

def turn_off():
    """ Turn off inline translations """
    global enabled
    enabled = False


def turn_on_for_session():
    """ Turn on and remember in cookies """
    global save
    turn_on()
    save = True

def turn_off_for_session():
    """ Turn off and remember in cookies """
    global save
    turn_off()
    save = True

def wrap_string(text):
    """ Wrap string with tranlation """
    global enabled
    if enabled:
            return u'<tml:label class="tr8n_translatable tr8n_translated">%s</tml:label>' % text
    return text
