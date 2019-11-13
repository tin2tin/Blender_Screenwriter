import re


class Underline(object):

    parse_re = re.compile(
        # underline
        r'_'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'([^_]+)'
        # finishing with underline
        r'(?<=\S)_'
    )

    start_html = '<u>'
    end_html = '</u>'


class Italic(object):

    parse_re = re.compile(
        # one star
        r'\*'
        # anything but a space, then text
        r'([^\s].*?)'
        # finishing with one star
        r'\*'
        # must not be followed by star
        r'(?!\*)'
    )

    start_html = '<em>'
    end_html = '</em>'


class Bold(object):

    parse_re = re.compile(
        # two stars
        r'\*\*'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'(.+?[*_]*)'
        # finishing with two stars
        r'(?<=\S)\*\*'
    )

    start_html = '<strong>'
    end_html = '</strong>'


class BoldItalic(object):

    parse_re = re.compile(
        # three stars
        r'\*\*\*'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'(.+?[*_]*)'
        # finishing with three stars
        r'(?<=\S)\*\*\*'
    )

    start_html = '<strong><em>'
    end_html = '</em></strong>'


class Asteriks(object):

    parse_re = re.compile(
        # one slash and one star
        r'\\\*'
        # must not be followed by space
        r'(?=\S)'
        # inside text
        r'(.+?[*_]*)'
        # finishing with one slash and one star
        r'(?<=\S)\\\*'
    )

    start_html = '&#42;'
    end_html = '&#42;'


styles = (Asteriks, BoldItalic, Bold, Italic, Underline)


def Fountain2HTML(text, plaintext=False):
    out = text
    if not plaintext:
        for x in styles:
            out = x.parse_re.sub(x.start_html + r'\1' + x.end_html, out)
    else:
        for x in styles:
            out = x.parse_re.sub(r'\1', out)
    return out
