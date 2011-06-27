# Created By: Virgil Dupras
# Created On: 2011-06-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from html import escape as html_escape

from .pdf import ElementState

RE_STARTING_NUMBER = re.compile(r'^(\d+)')

def link_footnotes(elements):
    """Adjust the text of footnotes and their linked text to add HTML anchors.
    """
    # The way we do this is that we first identify what number the footnote starts with (if it's not
    # a number, ignore it, we're not gonna link it. maybe later). Then, we look in all elemts
    # preceeding it for the first one (which is closest to the footnote) with that number in it.
    # For now, that's a bit basic because there are certainly cases where incorrect linking will
    # be made, but let's not get too complex too fast...
    # Also, footnotes get renumbered because some footnotes reset themselves suring an article.
    # Because we push all footnotes at the end, we don't want to end up with duplicate numbers.
    footnotes = [e for e in elements if e.state == ElementState.Footnote]
    for footnumber, footnote in enumerate(footnotes, start=1):
        m = RE_STARTING_NUMBER.match(footnote.text)
        if not m:
            # we can't link that, but we still want to prepend the footnote with footnumber
            footnote.text = '[{}] {}'.format(footnumber, footnote.text)
            continue
        [lookfor] = m.groups()
        re_lookfor = re.compile(r'(\D){}(\D|$)'.format(lookfor))
        index = elements.index(footnote)
        # we reverse because we want the element closest to the footnote. Also, we remove footnotes
        # because we don't want to mistakenly mink footnotes to other footnotes.
        the_rest = [e for e in reversed(elements[:index]) if e.state != ElementState.Footnote]
        for e in the_rest:
            m = re_lookfor.search(e.text)
            if m is None:
                continue
            [prevchar, nextchar] = m.groups()
            link = '<a name="linkback{0}"></a><a href="#footnote{0}">[{0}]</a>'.format(footnumber)
            e.text = re_lookfor.sub(prevchar+link+nextchar, e.text, count=1)
            link = '<a name="footnote{0}"></a><a href="#linkback{0}">[{0}]</a>'.format(footnumber)
            footnote.text = footnote.text.replace(lookfor, link, 1)
            break
        else:
            # we don't have a link, but we still want to put the footnumber in there
            footnote.text = footnote.text.replace(lookfor, '[{}]'.format(footnumber), 1)

def wrap(text, inside):
    return "<{1}>{0}</{1}>".format(html_escape(text), inside)

def generate_html(elements):
    elements = [e for e in elements if e.state != ElementState.Ignored]
    link_footnotes(elements)
    keyfunc = lambda e: 0 if e.state != ElementState.Footnote else 1
    elements.sort(key=keyfunc) # footnotes go last
    paragraphs = []
    for e in elements:
        if e.state == ElementState.Title:
            s = wrap(e.text, 'h1')
        else:
            s = wrap(e.text, 'p')
        paragraphs.append(s)
    s = '\n'.join(paragraphs)
    return "<html><body>\n{}\n</body></html>".format(s)