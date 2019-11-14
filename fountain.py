"""
fountain.py
Ported to Python 3 by Colton J. Provias - cj@coltonprovias.com
Original Python code at https://gist.github.com/ColtonProvias/8232624
Based on Fountain by Nima Yousefi & John August
Original code for Objective-C at https://github.com/nyousefi/Fountain
Further Edited by Manuel Senfft
"""


COMMON_TRANSITIONS = {'FADE OUT.', 'CUT TO BLACK.', 'FADE TO BLACK.'}


class FountainElement:
    def __init__(
        self,
        element_type,
        element_text='',
        section_depth=0,
        scene_number='',
        is_centered=False,
        is_dual_dialogue=False,
        original_line=0,
        scene_abbreviation='.',
        original_content=''
    ):
        self.element_type = element_type
        self.element_text = element_text
        self.section_depth = section_depth
        self.scene_number = scene_number
        self.scene_abbreviation = scene_abbreviation
        self.is_centered = is_centered
        self.is_dual_dialogue = is_dual_dialogue
        self.original_line = original_line
        self.original_content = original_content

    def __repr__(self):
        return self.element_type + ': ' + self.element_text


class Fountain:
    def __init__(self, string=None, path=None):
        self.metadata = dict()
        self.elements = list()

        if path:
            with open(path) as fp:
                self.contents = fp.read()
        else:
            self.contents = string
        if self.contents != '':
            self.parse()

    def parse(self):
        contents = self.contents.strip().replace('\r', '')

        contents_has_metadata = ':' in contents.splitlines()[0]
        contents_has_body = '\n\n' in contents

        if contents_has_metadata and contents_has_body:
            script_head, script_body = contents.split('\n\n', 1)
            self._parse_head(script_head.splitlines())
            self._parse_body(script_body.splitlines())
        elif contents_has_metadata and not contents_has_body:
            self._parse_head(contents.splitlines())
        else:
            self._parse_body(contents.splitlines())

    def _parse_head(self, script_head):
        open_key = None
        for line in script_head:
            line = line.rstrip()
            if line[0].isspace():
                self.metadata[open_key].append(line.strip())
            elif line[-1] == ':':
                open_key = line[0:-1].lower()
                self.metadata[open_key] = list()
            else:
                key, value = line.split(':', 1)
                self.metadata[key.strip().lower()] = [value.strip()]

    def _parse_body(self, script_body):
        is_comment_block = False
        is_inside_dialogue_block = False
        newlines_before = 0
        index = -1
        comment_text = list()

        for linenum, line in enumerate(script_body):
            assert type(line) is str
            index += 1
            line = line.lstrip()
            full_strip = line.strip()

            if (not line or line.isspace()) and not is_comment_block:
                self.elements.append(FountainElement('Empty Line'))
                is_inside_dialogue_block = False
                newlines_before += 1
                continue

            if line.startswith('/*'):
                line = line.rstrip()
                if line.endswith('*/'):
                    text = line.replace('/*', '').replace('*/', '')
                    self.elements.append(
                        FountainElement(
                            'Boneyard',
                            text,
                            original_line=linenum,
                            original_content=line
                        )
                    )
                    is_comment_block = False
                    newlines_before = 0
                else:
                    is_comment_block = True
                    comment_text.append('')
                continue

            if line.rstrip().endswith('*/'):
                text = line.replace('*/', '')
                comment_text.append(text.strip())
                self.elements.append(
                    FountainElement(
                        'Boneyard',
                        '\n'.join(comment_text),
                        original_line=linenum,
                        original_content=line
                    )
                )
                is_comment_block = False
                comment_text = list()
                newlines_before = 0
                continue

            if is_comment_block:
                comment_text.append(line)
                continue

            if line.startswith('==='):
                self.elements.append(
                    FountainElement(
                        'Page Break',
                        line,
                        original_line=linenum,
                        original_content=line
                    )
                )
                newlines_before = 0
                continue

            if len(full_strip) > 0 and full_strip[0] == '=':
                self.elements.append(
                    FountainElement(
                        'Synopsis',
                        full_strip[1:].strip(),
                        original_line=linenum,
                        original_content=line
                    )
                )
                continue

            if (
                newlines_before > 0 and
                full_strip.startswith('[[') and
                full_strip.endswith(']]')
            ):
                self.elements.append(
                    FountainElement(
                        'Comment',
                        full_strip.strip('[] \t'),
                        original_line=linenum,
                        original_content=line
                    )
                )
                continue

            if len(full_strip) > 0 and full_strip[0] == '#':
                newlines_before = 0
                depth = full_strip.split()[0].count('#')
                self.elements.append(
                    FountainElement(
                        'Section Heading',
                        full_strip[depth:],
                        section_depth=depth,
                        original_line=linenum,
                        original_content=line
                    )
                )
                continue

            if len(line) > 1 and line[0] == '.' and line[1] != '.':
                newlines_before = 0
                if full_strip[-1] == '#' and full_strip.count('#') > 1:
                    scene_number_start = len(full_strip) - \
                        full_strip[::-1].find('#', 1) - 1
                    self.elements.append(
                        FountainElement(
                            'Scene Heading',
                            full_strip[1:scene_number_start].strip(),
                            scene_number=full_strip[
                                scene_number_start:
                            ].strip('#').strip(),
                            original_line=linenum,
                            original_content=line
                        )
                    )
                else:
                    self.elements.append(
                        FountainElement(
                            'Scene Heading',
                            full_strip[1:].strip(),
                            original_line=linenum,
                            original_content=line
                        )
                    )
                continue

            if (
                line[0:4].upper() in
                ['INT ', 'INT.', 'EXT ', 'EXT.', 'EST ', 'EST.', 'I/E ', 'I/E.'] or
                line[0:8].upper() in ['INT/EXT ', 'INT/EXT.'] or
                line[0:9].upper() in ['INT./EXT ', 'INT./EXT.']
            ):
                newlines_before = 0
                scene_name_start = line.find(line.split()[1])
                if full_strip[-1] == '#' and full_strip.count('#') > 1:
                    scene_number_start = len(full_strip) - \
                        full_strip[::-1].find('#', 1) - 1
                    self.elements.append(
                        FountainElement(
                            'Scene Heading',
                            full_strip[
                                scene_name_start:scene_number_start
                            ].strip(),
                            scene_number=full_strip[
                                scene_number_start:
                            ].strip('#').strip(),
                            original_line=linenum,
                            scene_abbreviation=line.split()[0],
                            original_content=line
                        )
                    )
                else:
                    self.elements.append(
                        FountainElement(
                            'Scene Heading',
                            full_strip[scene_name_start:].strip(),
                            original_line=linenum,
                            scene_abbreviation=line.split()[0],
                            original_content=line
                        )
                    )
                continue

            if full_strip.endswith(' TO:'):
                newlines_before = 0
                self.elements.append(
                    FountainElement(
                        'Transition',
                        full_strip,
                        original_line=linenum,
                        original_content=line
                    )
                )
                continue

            if full_strip in COMMON_TRANSITIONS:
                newlines_before = 0
                self.elements.append(
                    FountainElement(
                        'Transition',
                        full_strip,
                        original_line=linenum,
                        original_content=line
                    )
                )
                continue

            if full_strip[0] == '>':
                newlines_before = 0
                if len(full_strip) > 1 and full_strip[-1]:
                    self.elements.append(
                        FountainElement(
                            'Action',
                            full_strip[1:-1].strip(),
                            is_centered=True,
                            original_line=linenum,
                            original_content=line
                        )
                    )
                else:
                    self.elements.append(
                        FountainElement(
                            'Transition',
                            full_strip[1:].strip(),
                            original_line=linenum,
                            original_content=line
                        )
                    )
                continue

            if (
                newlines_before > 0 and
                index + 1 < len(script_body) and
                script_body[index + 1] and
                not line[0] in ['[', ']', ',', '(', ')']
            ):
                newlines_before = 0
                if full_strip[-1] == '^':
                    for element in reversed(self.elements):
                        if element.element_type == 'Character':
                            element.is_dual_dialogue = True
                            break
                    self.elements.append(
                        FountainElement(
                            'Character',
                            full_strip.rstrip('^').strip(),
                            is_dual_dialogue=True,
                            original_line=linenum,
                            original_content=line
                        )
                    )
                    is_inside_dialogue_block = True
                else:
                    self.elements.append(
                        FountainElement(
                            'Character',
                            full_strip,
                            original_line=linenum,
                            original_content=line
                        )
                    )
                    is_inside_dialogue_block = True
                continue

            if is_inside_dialogue_block:
                if newlines_before == 0 and full_strip[0] == '(':
                    self.elements.append(
                        FountainElement(
                            'Parenthetical',
                            full_strip,
                            original_line=linenum,
                            original_content=line
                        )
                    )
                else:
                    if self.elements[-1].element_type == 'Dialogue':
                        self.elements[-1].element_text = '\n'.join(
                            [self.elements[-1].element_text, full_strip]
                        )
                    else:
                        self.elements.append(
                            FountainElement(
                                'Dialogue',
                                full_strip,
                                original_line=linenum,
                                original_content=line
                            )
                        )
                continue

            if newlines_before == 0 and len(self.elements) > 0:
                self.elements[-1].element_text = '\n'.join(
                    [self.elements[-1].element_text, full_strip])
                newlines_before = 0
            else:
                self.elements.append(
                    FountainElement(
                        'Action',
                        full_strip,
                        original_line=linenum,
                        original_content=line
                    )
                )
                newlines_before = 0
