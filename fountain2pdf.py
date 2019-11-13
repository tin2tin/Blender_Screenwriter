import fountain2pdf_style_radioplay as style  # define your style here

#import fountain2pdf_generate_soundlist
from fountain2pdf_2html import Fountain2HTML

from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer

#from fountain import fountain
import fountain

import sys
import os
import re

DEFAULT_AUTHOR = 'Manuel Senfft'


# if this string is set, only the whole script ABOVE this string will be rendered
only_above = '\n# ToDo'
path_to_project = os.path.dirname(os.path.realpath(__file__))

# functions


def getProgrammParameters(arr):
    # quit, if there is not at least one parameter
    if len(arr) < 2:
        print('At least one parameter needed: source fountain file.')
        #sys.exit
        return False

    # help print
    if '-h' in arr or '-help' in arr:
        print()
        print('A Fountain-script to PDF converter.')
        print('\t1st parameter: filename of the source fountain file')
        print(
            '\t-c / -char ["Character Name" / "all"] --> '
            'marks one char or all in seperate files'
        )
        print(
            '\t-co / -char-only ["Character Name"] --> '
            'prints out text for this character only'
        )
        print('\t-n / -notes --> enables output for comments/notes')
        print('\t-s / -soundlist --> outputs a soundlist only')
        print('\t-i / -index --> enables first page as index of sections and scenes')
        print('\t-d / -numbers --> enables numbers on the sounds / action sentences')
        print()
        exit()

    # quit, if the given parameter is not a file
    if not os.path.isfile(arr[1]):
        print(arr[1] + ' is not a valid file.')
        exit()

    # check parameters and assign default values
    output = {}

    # the file
    output['file'] = arr[1]

    # the characters
    if '-c' in arr:
        try:
            output['char'] = arr[arr.index('-c') + 1]
        except Exception:
            output['char'] = None
    elif '-char' in arr:
        try:
            output['char'] = arr[arr.index('-char') + 1]
        except Exception:
            output['char'] = None
    else:
        output['char'] = None

    # one character only
    if '-co' in arr:
        try:
            output['char_only'] = arr[arr.index('-co') + 1]
        except Exception:
            output['char_only'] = None
    elif '-char-only' in arr:
        try:
            output['char_only'] = arr[arr.index('-char_only') + 1]
        except Exception:
            output['char_only'] = None
    else:
        output['char_only'] = None

    # the notes
    if '-n' in arr or '-notes' in arr:
        output['notes'] = True
    else:
        output['notes'] = False

    # # the soundlist
    # if '-s' in arr or '-soundlist' in arr:
        # output['soundlist'] = True
    # else:
        # output['soundlist'] = False

    # the index
    if '-i' in arr or '-index' in arr:
        output['index'] = True
    else:
        output['index'] = False

    # the numbers
    if '-d' in arr or '-numbers' in arr:
        output['numbers'] = True
    else:
        output['numbers'] = False

    # return the output
    return output


def zero(number, total):
    # number has 1 digit
    if number < 10:
        if total > 9999:
            return '0000' + str(number)
        elif total > 999:
            return '000' + str(number)
        elif total > 99:
            return '00' + str(number)
        elif total > 9:
            return '0' + str(number)
        else:
            return str(number)

    # number has 2 digits
    elif number < 100:
        if total > 9999:
            return '000' + str(number)
        elif total > 999:
            return '00' + str(number)
        elif total > 99:
            return '0' + str(number)
        else:
            return str(number)

    # number has 3 digits
    elif number < 1000:
        if total > 9999:
            return '00' + str(number)
        elif total > 999:
            return '0' + str(number)
        else:
            return str(number)

    # number has 4 digits
    elif number < 10000:
        if total > 9999:
            return '0' + str(number)
        else:
            return str(number)


def getCharacters(fount):
    chars = []

    # iterate through elements
    for f in fount.elements:
        if f.element_type == 'Character' and f.element_text.upper() not in chars:
            chars.append(f.element_text.upper())
    return chars


def countActionSentences(fount):
    count = 0
    for x in fount.elements:
        if x.element_type == 'Action' and '*Musik:' not in x.element_text:
            for sentence in re.split('(?<=[.!?]) +', x.element_text):
                count += 1
    return count


def generateIndex(fount):
    # generates an index with linking from section and scene headings
    # TODO: Does not work with links over the same page !!!

    out = []
    section_count = 0
    scene_count = 0
    for f in fount.elements:
        if f.element_type == 'Section Heading':
            out.append(
                Paragraph(
                    '<a href = section' + str(section_count) +
                    '><u>' + f.element_text + '</u></a>',
                    style.STYLE_INDEX_SECTION
                )
            )
            section_count += 1
        elif f.element_type == 'Scene Heading':
            out.append(
                Paragraph(
                    '<a href = scene' + str(scene_count) + '><u>' +
                    f.element_text + ' # ' + f.scene_number + '</u></a>',
                    style.STYLE_INDEX_SCENE
                )
            )
            scene_count += 1
    out.append(PageBreak())

    return out


def resetLeftSpace():
    return style.DOC_SIZE[1] - style.TOPMARGIN - style.BOTTOMMARGIN - style.SIZE


def getParaHeight(para, with_space=True):
    height = 0
    if with_space:
        height += para.getSpaceBefore()
        height += para.getSpaceAfter()

    height += para.wrap(style.DOC_SIZE[0], style.DOC_SIZE[1])[1]

    return height


def generateTitlepage(fount):
    # generate title page
    at_least_one_metadata = False
    para_title = None
    para_credit = None
    para_author = None
    para_date = None
    para_contact = None
    left_space = resetLeftSpace()
    for meta in iter(fount.metadata.items()):
        # get title
        if meta[0] == 'title':
            at_least_one_metadata = True
            para_title = Paragraph(
                Fountain2HTML('<br />' + '<br />' + '<br />'.join(meta[1])),
                style.STYLE_TITLEPAGE_TITLE
            )
            left_space -= getParaHeight(para_title)

        # get credit
        elif meta[0] == 'credit' or meta[0] == 'credits':
            at_least_one_metadata = True
            para_credit = Paragraph(
                Fountain2HTML('<br />'.join(meta[1])),
                style.STYLE_TITLEPAGE_CREDIT
            )
            left_space -= getParaHeight(para_credit)

        # get author
        elif meta[0] == 'author' or meta[0] == 'authors':
            at_least_one_metadata = True
            para_author = Paragraph(
                Fountain2HTML('<br />'.join(meta[1])),
                style.STYLE_TITLEPAGE_AUTHOR
            )
            left_space -= getParaHeight(para_author)

        # get date
        elif meta[0] == 'date':
            at_least_one_metadata = True
            para_date = Paragraph(
                Fountain2HTML('<br />'.join(meta[1])),
                style.STYLE_TITLEPAGE_DATE
            )
            left_space -= getParaHeight(para_date)

        # get contact
        elif meta[0] == 'contact':
            at_least_one_metadata = True
            para_contact = Paragraph(
                Fountain2HTML('<br />'.join(meta[1])),
                style.STYLE_TITLEPAGE_CONTACT
            )
            left_space -= getParaHeight(para_contact)

    # output
    out = []
    if at_least_one_metadata:
        if para_title:
            out.append(para_title)
        if para_credit:
            out.append(para_credit)
        if para_author:
            out.append(para_author)
        if para_date:
            out.append(Spacer(0, left_space))
            out.append(para_date)
        if not para_date and para_contact:
            out.append(Spacer(0, left_space))
            out.append(para_contact)
        elif para_date and para_contact:
            out.append(para_contact)
        out.append(PageBreak())

    return out


def genSceneId(fount_element):
    out = ''
    if fount_element.element_type == 'Scene Heading':
        out += str(fount_element.scene_number)
        out += fount_element.element_text
        return out
    else:
        return False


def getCharonlyScenes(fount, charonly):
    scenes = []
    for f in fount.elements:
        if f.element_type == 'Scene Heading':
            active_scene = genSceneId(f)
        if f.element_type == 'Character' and charonly is not None:
            if charonly.upper() == f.element_text:
                scenes.append(active_scene)
    return scenes


def Fountain2PDF(fount, char=None, charonly=None):
    # generate filename
    if charonly is None:
        if char and char.upper() in getCharacters(fount):
            char = char.upper()
            out_filename = PAR['file'].replace(
                '.fountain', '_' + char.replace(' ', '_') + '.pdf'
            )
            mark = True
        else:
            out_filename = PAR['file'].replace('.fountain', '.pdf')
            mark = False
    else:
        if charonly and charonly.upper() in getCharacters(fount):
            charonly = charonly.upper()
            out_filename = PAR['file'].replace(
                '.fountain', '_' + charonly.replace(' ', '_') + '_ONLY.pdf'
            )
            # still mark it, when -c is set as well
            if type(char) == str and char.upper() == charonly.upper():
                mark = True
            else:
                mark = False
        else:
            out_filename = PAR['file'].replace('.fountain', '.pdf')
            mark = False

    # get scenes for charonly character
    charonly_scenes = getCharonlyScenes(fount, charonly)

    # generate doc and empty output-array
    doc = SimpleDocTemplate(
        out_filename,
        pagesize=style.DOC_SIZE,
        rightMargin=style.RIGHTMARGIN,
        leftMargin=style.LEFTMARGIN,
        topMargin=style.TOPMARGIN,
        bottomMargin=style.BOTTOMMARGIN
    )
    Story = []

    # make titlepage
    Story.extend(generateTitlepage(fount))

    # make index, if enabled
    if PAR['index']:
        Story.extend(generateIndex(fount))

    # some variables before iteration starts
    skip_empty_line = False
    mark_char = False
    charonly_active = None
    section_count = 0
    scene_count = 0
    action_sentence = 1
    action_total = countActionSentences(fount)

    # iterate through every fountain element
    for fc, f in enumerate(fount.elements):

        # it is a section heading
        if (
            f.element_type == 'Section Heading' and
            f.section_depth < 3
        ):
            # generate anchor for index linking for sections
            tmp_section_anchor = '<a name = section' + str(section_count) + ' /> '
            section_count += 1
            para_tmp = Paragraph(
                tmp_section_anchor + f.element_text, style.STYLE_SECTION_HEADING
            )
            Story.append(para_tmp)
            skip_empty_line = False

        # it is a scene heading
        elif f.element_type == 'Scene Heading':
            if charonly is None or genSceneId(f) in charonly_scenes:
                # print scene number on the left, if enabled
                if style.SCENE_NUMBER_L:
                    para_tmp = Paragraph(
                        f.scene_number if f.scene_number != '' else'&nbsp;',
                        style.STYLE_SCENE_NUMBER_L
                    )
                    Story.append(para_tmp)
                # get scene abbreviation and print it, if it is not a dot
                tmp_scene_abb = (
                    f.scene_abbreviation + ' ' if f.scene_abbreviation != '.' else ''
                )
                # generate anchor for index linking for scenes
                tmp_scene_anchor = '<a name = scene' + str(scene_count) + ' /> '
                scene_count += 1
                para_tmp = Paragraph(
                    tmp_scene_anchor + tmp_scene_abb +
                    f.element_text, style.STYLE_SCENE_HEADING
                )
                Story.append(para_tmp)
                # print scene number on the left, if enabled
                if style.SCENE_NUMBER_R:
                    para_tmp = Paragraph(
                        f.scene_number if f.scene_number != '' else
                        '&nbsp;', style.STYLE_SCENE_NUMBER_R
                    )
                    Story.append(para_tmp)
                skip_empty_line = False
            else:
                skip_empty_line = True

        # it is a comment / a note
        elif f.element_type == 'Comment':
            if PAR['notes']:
                para_tmp = Paragraph(
                    '[ ' + Fountain2HTML(f.element_text) +
                    ' ]', style.STYLE_COMMENT
                )
                Story.append(para_tmp)
            else:
                skip_empty_line = True

        # it is action
        elif f.element_type == 'Action':
            if charonly is None:
                tmp_action = ''
                if PAR['numbers'] and '*Musik:' not in f.element_text:
                    RE = re.split('(?<=[.!?]) +', f.element_text)
                    for sentnum, sentence in enumerate(RE):
                        if sentnum >= 0 and sentnum <= len(RE):
                            tmp_space = ' '
                        else:
                            tmp_space = ''
                        tmp_action += (
                            '<strong>' + zero(action_sentence, action_total) +
                            ':</strong> ' + sentence + tmp_space
                        )
                        action_sentence += 1
                else:
                    tmp_action = f.element_text
                para_tmp = Paragraph(Fountain2HTML(tmp_action), style.STYLE_ACTION)
                Story.append(para_tmp)
                skip_empty_line = False
            else:
                skip_empty_line = True

        # it is a character
        elif f.element_type == 'Character':
            if charonly is None or f.element_text == charonly.upper():
                if mark and (f.element_text == char or f.element_text == charonly):
                    para_tmp = Paragraph(f.element_text, style.STYLE_CHARACTER_MARK)
                    Story.append(para_tmp)
                    mark_char = True
                else:
                    para_tmp = Paragraph(f.element_text, style.STYLE_CHARACTER)
                    Story.append(para_tmp)
                    mark_char = False
                charonly_active = f.element_text
                skip_empty_line = False
            else:
                charonly_active = None

        # it is a parenthetical
        elif f.element_type == 'Parenthetical':
            if charonly is None or charonly_active == charonly.upper():
                if mark and mark_char:
                    para_tmp = Paragraph(
                        Fountain2HTML(f.element_text), style.STYLE_PARENTHETICAL_MARK
                    )
                    Story.append(para_tmp)
                else:
                    para_tmp = Paragraph(
                        Fountain2HTML(f.element_text), style.STYLE_PARENTHETICAL
                    )
                    Story.append(para_tmp)
                skip_empty_line = False
            else:
                skip_empty_line = True

        # it is dialogue
        elif f.element_type == 'Dialogue':
            if charonly is None or charonly_active == charonly.upper():
                if mark and mark_char:
                    para_tmp = Paragraph(
                        Fountain2HTML(f.element_text), style.STYLE_DIALOGUE_MARK
                    )
                    Story.append(para_tmp)
                else:
                    para_tmp = Paragraph(
                        Fountain2HTML(f.element_text), style.STYLE_DIALOGUE
                    )
                    Story.append(para_tmp)
                skip_empty_line = False
            else:
                skip_empty_line = True

        # it is a transition
        elif f.element_type == 'Transition':
            if charonly is None:
                para_tmp = Paragraph(f.element_text, style.STYLE_TRANSITION)
                Story.append(para_tmp)
                skip_empty_line = False
            else:
                skip_empty_line = True

        # it is an empty line
        elif f.element_type == 'Empty Line':
            if style.PRINT_EMPTY_LINES and not skip_empty_line:
                para_tmp = Paragraph('&nbsp;', style.STYLE_EMPTY_LINE)
                Story.append(para_tmp)
                skip_empty_line = False

        # it is a page break
        elif f.element_type == 'Page Break':
            Story.append(PageBreak())
            skip_empty_line = False

        # it is a synopsis
        elif f.element_type == 'Synopsis':
            if PAR['notes']:
                para_tmp = Paragraph(
                    '~ ' + Fountain2HTML(f.element_text) + ' ~', style.STYLE_SYNOPSIS
                )
                Story.append(para_tmp)
            else:
                skip_empty_line = True

        # it is a boneyard
        elif f.element_type == 'Boneyard':
            # do nothing ... it's just the outcommented boneyard
            pass

    # get title
    if 'title' in fount.metadata:
        doc.title = ', '.join(
            [Fountain2HTML(x, True) for x in fount.metadata['title']]
        )
    else:
        if char:
            doc.title = PAR['file'].replace('.fountain', ': ' + char)
        else:
            doc.title = PAR['file'].replace('.fountain', '')

    # get author
    if 'author' in fount.metadata:
            doc.author = ', '.join(
                [Fountain2HTML(x, True) for x in fount.metadata['author']]
            )
    else:
        doc.author = DEFAULT_AUTHOR
    doc.creator = doc.author

    # get description
    if 'subject' in fount.metadata:
        doc.subject = ', '.join(
            [Fountain2HTML(x, True) for x in fount.metadata['subject']]
        )

    # get tags
    if 'tags' in fount.metadata:
        doc.keywords = fount.metadata['tags']
    elif 'tag' in fount.metadata:
        doc.keywords = fount.metadata['tag']
    elif 'keywords' in fount.metadata:
        doc.keywords = fount.metadata['keywords']
    elif 'keyword' in fount.metadata:
        doc.keywords = fount.metadata['keyword']

    # save to PDF
    doc.build(Story)  # , canvasmaker=NumberedCanvas)  # disabled, since it breaks links


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont(style.FONT, style.SIZE)
        self.setFillColorRGB(.5, .5, .5)
        self.drawRightString(
            570, 20, "%d / %d" % (self._pageNumber, page_count)
        )


def getLocations(SFXList):
    locs = []
    for x in SFXList:
        for y in x.locations:
            if y not in locs:
                locs.append(y)
    return locs


# def Fountain2SoundlistPDF(fount):
    # Story = []

    # # get / generate list of sounds
    # SOUNDS = fountain2pdf_generate_soundlist.generateSoundlist(PAR['file'])
    # AMOUNT = len(SOUNDS)

    # # get locations
    # LOCATIONS = sorted(getLocations(SOUNDS))

    # # generate index for locations
    # loc_num = 0
    # for x in LOCATIONS:
        # # x = x.decode(encoding='UTF-8')
        # Story.append(
            # Paragraph(
                # '<a href = location' + str(loc_num) + '><u>' +
                # x + '</u></a>', style.STYLE_INDEX_LOCATION
            # )
        # )
        # loc_num += 1
    # Story.append(PageBreak())

    # # generate doc and empty output-array
    # doc = SimpleDocTemplate(
        # PAR['file'].replace('.fountain', '_SFX.pdf'),
        # pagesize=style.DOC_SIZE,
        # rightMargin=style.RIGHTMARGIN,
        # leftMargin=style.LEFTMARGIN,
        # topMargin=style.TOPMARGIN,
        # bottomMargin=style.BOTTOMMARGIN
    # )

    # # iterate through locations and add sounds to the pages
    # loc_num = 0
    # for loc in LOCATIONS:
        # # loc = loc.decode(encoding='UTF-8')
        # Story.append(
            # Paragraph(
                # '<a name = location' + str(loc_num) +
                # ' />Location:<br /><br /><br /><b>' + loc +
                # '</b>', style.STYLE_SOUNDLIST_LOCATION_HEAD
            # )
        # )
        # loc_num += 1
        # Story.append(PageBreak())

        # # iter through all sounds and add one sound per page, if it's in the location
        # for sfx in SOUNDS:
            # # if loc in [x.decode(encoding='UTF-8') for x in sfx.locations]:
            # if loc in sfx.locations:
                # Story.append(Paragraph(loc, style.STYLE_SOUNDLIST_LOCATION))
                # Story.append(Paragraph('&nbsp;', style.STYLE_SOUNDLIST_LOCATION))
                # Story.append(
                    # Paragraph(
                        # sfx.scenenumber + ' - ' + sfx.scene +
                        # ' - ' + sfx.scenenumber, style.STYLE_SOUNDLIST_SCENE
                    # )
                # )
                # Story.append(
                    # Paragraph(
                        # '( ' + zero(sfx.number, AMOUNT) + ' )  ' +
                        # sfx.sound, style.STYLE_SOUNDLIST_SOUND
                    # )
                # )
                # Story.append(PageBreak())

    # # get title
    # if 'title' in fount.metadata:
        # doc.title = ', '.join(
            # [Fountain2HTML(x, True) for x in fount.metadata['title']]
        # ) + ': SFX'
    # else:
        # doc.title = PAR['file'].replace('.fountain', ': SFX')

    # # get author
    # if 'author' in fount.metadata:
            # doc.author = ', '.join(
                # [Fountain2HTML(x, True) for x in fount.metadata['author']]
            # )
    # else:
        # doc.author = DEFAULT_AUTHOR
    # doc.creator = doc.author

    # # get description
    # if 'subject' in fount.metadata:
        # doc.subject = ', '.join(
            # [Fountain2HTML(x, True) for x in fount.metadata['subject']]
        # )

    # # get tags
    # if 'tags' in fount.metadata:
        # doc.keywords = fount.metadata['tags']
    # elif 'tag' in fount.metadata:
        # doc.keywords = fount.metadata['tag']
    # elif 'keywords' in fount.metadata:
        # doc.keywords = fount.metadata['keywords']
    # elif 'keyword' in fount.metadata:
        # doc.keywords = fount.metadata['keyword']

    # # save to PDF
    # doc.build(Story)  # , canvasmaker=NumberedCanvas)  # disabled, since it breaks links


# START THE PROGRAMM

# get parameter settings
PAR = getProgrammParameters(sys.argv)

if PAR != False:

    # load fountain file
    d = open(PAR['file'], 'r')
    work_with_me = d.read()
    d.close()

    # read only above the given string (only_above)
    if only_above != '' and only_above != ' ':
        this_text = work_with_me[:work_with_me.find(only_above)]
    else:
        this_text = work_with_me

    # make it a fountain object
    F = fountain.Fountain(this_text)


    # # check if it should output soundlist or not
    # if PAR['soundlist']:
        # Fountain2SoundlistPDF(F)

    # do normal script rendering
    #else:

    # check if it should output all characters automatically or not
    if PAR['char'] == 'all':
        Fountain2PDF(F, charonly=PAR['char_only'])
        for x in getCharacters(F):
            Fountain2PDF(F, x, charonly=PAR['char_only'])

    # make a single script render
    else:
        Fountain2PDF(F, PAR['char'], charonly=PAR['char_only'])