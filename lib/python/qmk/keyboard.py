"""Functions that help us work with keyboards.
"""
from array import array
from glob import glob
from math import ceil
from pathlib import Path

from milc import cli

from qmk.c_parse import find_layouts, parse_config_h_file
from qmk.makefile import parse_rules_mk_file


def is_keyboard(keyboard_folder):
    """Returns True if keyboard is a valid keyboard_folder.
    """
    keyboard_folder = Path('keyboards') / keyboard_folder
    rules = keyboard_folder / 'rules.mk'
    return keyboard_folder.exists() and rules.exists()


def config_h(keyboard):
    """Parses all the config_h.mk files for a keyboard.

    Args:
        keyboard: name of the keyboard

    Returns:
        a dictionary representing the content of the entire rules.mk tree for a keyboard
    """
    keyboard = Path(keyboard)
    rules = rules_mk(keyboard)
    cur_dir = Path('keyboards')
    config = {}

    if 'DEFAULT_FOLDER' in rules:
        keyboard = rules['DEFAULT_FOLDER']

    for dir in keyboard.parts:
        cur_dir = cur_dir / dir
        config = {**config, **parse_config_h_file(cur_dir / 'config.h')}

    return config


def rules_mk(keyboard):
    """Get a rules.mk for a keyboard

    Args:
        keyboard: name of the keyboard

    Returns:
        a dictionary representing the content of the entire rules.mk tree for a keyboard
    """
    keyboard = Path(keyboard)
    cur_dir = Path('keyboards')
    rules = {}

    if 'DEFAULT_FOLDER' in rules:
        keyboard = rules['DEFAULT_FOLDER']

    for dir in keyboard.parts:
        cur_dir = cur_dir / dir
        rules = {**rules, **parse_rules_mk_file('keyboards/%s/rules.mk' % keyboard)}

    return rules


def render_layout(layout_data, key_labels=None):
    """Renders a single layout.
    """
    textpad = [array('u', ' ' * 200) for x in range(50)]

    for key in layout_data:
        x = ceil(key.get('x', 0) * 4)
        y = ceil(key.get('y', 0) * 3)
        w = ceil(key.get('w', 1) * 4)
        h = ceil(key.get('h', 1) * 3)

        if key_labels:
            label = key_labels.pop(0)
            if label.startswith('KC_'):
                label = label[3:]
        else:
            label = key.get('label', '')

        label_len = w - 2
        label_leftover = label_len - len(label)

        if len(label) > label_len:
            label = label[:label_len]

        label_blank = ' ' * label_len
        label_border = '─' * label_len
        label_middle = label + ' '*label_leftover  # noqa: yapf insists there be no whitespace around *

        top_line = array('u', '┌' + label_border + '┐')
        lab_line = array('u', '│' + label_middle + '│')
        mid_line = array('u', '│' + label_blank + '│')
        bot_line = array('u', '└' + label_border + "┘")

        textpad[y][x:x + w] = top_line
        textpad[y + 1][x:x + w] = lab_line
        for i in range(h - 3):
            textpad[y + i + 2][x:x + w] = mid_line
        textpad[y + h - 1][x:x + w] = bot_line

    lines = []
    for line in textpad:
        if line.tounicode().strip():
            lines.append(line.tounicode().rstrip())

    return '\n'.join(lines)


def render_layouts(info_json):
    """Renders all the layouts from an `info_json` structure.
    """
    layouts = {}

    for layout in info_json['layouts']:
        layout_data = info_json['layouts'][layout]['layout']
        layouts[layout] = render_layout(layout_data)

    return layouts
