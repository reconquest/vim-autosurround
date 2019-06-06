# coding=utf8

from contextlib import contextmanager
import vim
import re

import logging as log

_current_pairs = {}

RE_CLOSING_PAIRS = r'^[)}"\]]+$'
RE_OPENING_PAIRS = r'^[\(\{"\[]+$'

PAIRS = {
    '(': ')',
    '{': '}',
    '[': ']',
    '"': '"',
    "'": "'"
}

BRACKETS = {
    '(': ')',
    '{': '}',
    '[': ']',
}


def enable_debug_log():
    log.basicConfig(
        filename='/tmp/autosurround.log',
        filemode='w',
        format='%(levelname)s - %(message)s',
        level=log.DEBUG
    )


def insert_new_line():
    cursor = _get_cursor()

    indent = vim.Function('indent')(cursor[0])
    tabwidth = vim.Function('shiftwidth')()

    in_brackets = _is_cursor_between_brackets()

    expandtab = int(vim.eval('&expandtab'))
    if not expandtab:
        symbol = '\t'
        shift = indent/tabwidth
        next_shift = shift
        if in_brackets:
            next_shift += 1
    else:
        symbol = ' '
        shift = indent
        next_shift = shift
        if in_brackets:
            next_shift += tabwidth

    if not in_brackets:
        _insert_new_line_at_cursor(1, shift*symbol)
        _set_cursor(cursor[0]+1, shift)
        return

    _insert_new_line_at_cursor(2, shift*symbol)
    vim.current.buffer[cursor[0]] = (next_shift * symbol)
    _set_cursor(cursor[0]+1, next_shift)

    # _insert_at_cursor(next_shift * symbol)


def _is_cursor_between_brackets():
    cursor = _get_cursor()
    line = vim.current.buffer[cursor[0] - 1]
    if cursor[1] < 1:
        return False

    open_bracket = line[cursor[1]-1]
    if open_bracket not in BRACKETS:
        return False

    close_bracket = BRACKETS[open_bracket]
    if len(line) > cursor[1]:
        cursor_char = line[cursor[1]]
        if cursor_char != close_bracket:
            return False

    return (open_bracket, close_bracket)


def surround(open_pair, close_pair):
    cursor = _get_cursor()

    try:
        end_pos = find_enclosure(cursor)
        if not end_pos:
            return False
    finally:
        _insert_at_cursor(open_pair)

    vim.command('let &undolevels = &undolevels')

    with _restore_cursor():
        _set_cursor(end_pos[0], end_pos[1])
        _insert_at_cursor(close_pair)

    buffer = vim.current.buffer
    _current_pairs[(buffer.number, cursor, close_pair)] = (
        end_pos[0],
        end_pos[1]
    )

    return True


def find_enclosure(cursor):
    for strategy in enclosing_strategies:
        if strategy is None:
            continue

        pos = strategy(cursor)
        if pos is not None:
            # print(strategy)
            return pos

def correct_inserted_pair(open_pair, close_pair):
    buffer = vim.current.buffer

    for pair in _current_pairs:
        corrected = False

        close_pair_pos = _current_pairs[pair]

        if len(buffer) < close_pair_pos[0] - 1:
            continue

        if len(buffer[close_pair_pos[0] - 1]) <= close_pair_pos[1]:
            continue

        if buffer[close_pair_pos[0] - 1][close_pair_pos[1]] != close_pair:
            continue

        moved = _delete_at(close_pair_pos, 1)

        try:
            with _restore_cursor():
                cursor = _get_cursor()
                line = buffer[cursor[0] - 1]
                if line[cursor[1] - 1] == close_pair:
                    _set_cursor(cursor[0], cursor[1] - 1)

                open_pair_pos = vim.Function('searchpairpos')(
                    _escape_open_pair(open_pair),
                    "",
                    close_pair,
                    "nb",
                )

            open_pair_pos = (
                int(open_pair_pos[0]),
                int(open_pair_pos[1]) - 1
            )

            if open_pair_pos <= (0, 0):
                continue

            current_pair = (buffer.number, open_pair_pos, close_pair)

            if current_pair not in _current_pairs:
                continue

            if _current_pairs[current_pair] == close_pair_pos:
                corrected = True
        finally:
            if not corrected:
                _insert_at(close_pair_pos, close_pair)
                if moved:
                    _move_cursor_relative(0, 1)
            else:
                _insert_at_cursor(close_pair)
                del _current_pairs[pair]
                return True

    return False


def correct_pair(open_pair, close_pair):
    if correct_inserted_pair(open_pair, close_pair):
        return True

    if skip_matching_pair(open_pair, close_pair):
        return False

    _insert_at_cursor(close_pair)

    return True


def skip_matching_pair(open_pair, close_pair):
    with _restore_cursor():
        cursor = (
            vim.current.window.cursor[0],
            vim.current.window.cursor[1]
        )

        next = vim.current.buffer[cursor[0] - 1][cursor[1]:]

        if len(next) == 0:
            return False

        if next[0] != close_pair:
            return False

        vim.command('normal! %')

        new_cursor = (
            vim.current.window.cursor[0],
            vim.current.window.cursor[1]
        )

    if new_cursor != cursor:
        vim.current.window.cursor = (
            cursor[0],
            cursor[1] + 1
        )

        return True

    return False


def clean_current_pairs():
    global _current_pairs
    cursor = vim.current.window.cursor
    cursor = (cursor[0], cursor[1] + 1)

    kept_pairs = {}
    for open_pair in _current_pairs:
        open_pair_pos = open_pair[0]
        close_pair_pos = _current_pairs[open_pair]
        if open_pair_pos <= cursor <= close_pair_pos or \
                cursor[0] == close_pair_pos[0]:
            kept_pairs[open_pair] = close_pair_pos

    _current_pairs = kept_pairs


def remove_pair():
    cursor = _get_cursor()

    # current cursor should be at least on 2nd position (start with 0)
    # to find a pair
    if cursor[1] < 1:
        return

    line = vim.current.buffer[cursor[0] - 1]

    match = re.match(RE_OPENING_PAIRS, line[cursor[1]-1])
    if not match:
        return

    open_pair = match.group(0)[0]
    close_pair = PAIRS[open_pair]
    _remove_pair(open_pair, close_pair)


def _remove_pair(open_pair, close_pair):
    pair_pos = vim.Function('searchpairpos')(
        _escape_open_pair(open_pair),
        "",
        close_pair,
        "n",
    )

    if pair_pos[0] == 0:
        return

    pair_pos = (
        pair_pos[0],
        pair_pos[1] - 1
    )

    _delete_at(pair_pos, 1)


def _match_enclosing_quote(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    if len(line) < 1:
        return

    match = re.match(r"(['\"`]).*", line)
    if not match:
        return

    if not _is_cursor_in_string((cursor[0], cursor[1] + 1)):
        return

    if cursor[1] > 0:
        if _is_cursor_in_string((cursor[0], cursor[1] - 1)):
            return

    old_cursor = vim.current.window.cursor

    with _restore_selection_register():
        with _restore_cursor():
            vim.command("normal! \"_va{}\033".format(match.group(1)))
            if vim.current.window.cursor > old_cursor:
                return (
                    vim.current.window.cursor[0],
                    vim.current.window.cursor[1] + 2
                )


def _match_long_identifier(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^([.\w_\[\]-]+)\s', line)
    if not match:
        return

    if match.group(1).count(']') != match.group(1).count('['):
        return

    if _is_cursor_in_string(cursor):
        return

    return (cursor[0], cursor[1] + len(match.group(1)) + 1)


def _match_enclosing_brace(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^(\[[.\w_\[\]-]+|[.\w_-]*)[([{]', line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    with _restore_cursor():
        vim.current.window.cursor = cursor
        vim.command('normal! {}%'.format(
            (str(len(match.group(1))) + 'l') if match.group(1) != '' else ''
        ))

        cursor = (
            vim.current.window.cursor[0],
            vim.current.window.cursor[1] + 1
        )

        line = vim.current.buffer[cursor[0] - 1][cursor[1]:]

        if re.match(r'^[\w{([]', line):
            return _match_enclosing_brace(cursor)

        return (cursor[0], cursor[1]+1)


def _match_stopper(cursor):
    """
    returns current cursor position if any stopper found in the end of line
    stopper can be something like = ; , or a space
    handles cases like
    a[b.c|] = d
    press [
    causes plugin return position before ]
    """
    if _is_cursor_in_string(cursor):
        return

    if len(vim.current.buffer[cursor[0] - 1]) == cursor[1]:
        return

    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    for index in range(len(line)):
        if line[index] in '}])"\']`;=,':
            return (cursor[0], cursor[1]+1+index)

    return


def _match_end_of_code_block(cursor):
    if _is_cursor_in_string(cursor):
        return

    if len(vim.current.buffer[cursor[0] - 1]) == cursor[1]:
        return

    if vim.current.buffer[cursor[0] - 1][-1] in '{[("\'`':
        return

    if len(vim.current.buffer) > cursor[0]:
        next_line = vim.current.buffer[cursor[0]].strip()
        if next_line == '}' or next_line == '':
            line = vim.current.buffer[cursor[0] - 1]
            matches = re.match(r'^(.*?)[:}]?$', line)
            return (cursor[0], len(matches.group(1)) + 1)


def _match_end_of_line(cursor):
    if _is_cursor_in_string(cursor):
        return

    line = vim.current.buffer[cursor[0] - 1]

    if len(line) != cursor[1]:
        matches = re.match(r'^[)"\]]+$', line[cursor[1]:])
        if not matches:
            return

    return (cursor[0], cursor[1]+1)


def _match_argument(cursor):
    if _is_cursor_in_string(cursor):
        return

    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]

    matches = re.match(r'([\w.]+)[,)\]]', line)
    if not matches:
        return

    return (cursor[0], cursor[1] + len(matches.group(1)) + 1)


def _match_semicolon(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^(.*);', line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    return (cursor[0], cursor[1] + len(match.group(1)))


def register_finder(callback):
    enclosing_strategies.append(callback)
    return len(enclosing_strategies)


def unregister_finder(index):
    enclosing_strategies[index] = None


@contextmanager
def _restore_cursor():
    cursor = vim.current.window.cursor
    yield
    vim.current.window.cursor = cursor


@contextmanager
def _restore_selection_register():
    cursor = vim.current.window.cursor
    yield
    vim.current.window.cursor = cursor


def _is_cursor_in_string(cursor):
    synstack = vim.Function('synstack')(
        cursor[0],
        cursor[1] + 1
    )

    for syn_id in synstack:
        syn_name = vim.Function('synIDattr')(
            vim.Function('synIDtrans')(syn_id),
            "name",
        )
        if syn_name.lower() == 'string':
            return True
            break

    return False


def _insert_at_cursor(text):
    cursor = _get_cursor()

    _insert_at(cursor, text)

    _set_cursor(
        cursor[0],
        cursor[1] + len(text)
    )


def _insert_new_line_at_cursor(count, indentation):
    cursor = _get_cursor()
    line   = cursor[0] - 1
    column = cursor[1]

    # adding empty line so lines can be easily moved after new line
    for _ in range(count):
        vim.current.buffer.append("")

    move_start = line + count
    move_end = len(vim.current.buffer) - 1

    text = vim.current.buffer[line][:]

    vim.current.buffer[line] = text[:column]

    target = move_end
    while target > move_start:
        target_text = vim.current.buffer[target-count]
        vim.current.buffer[target] = target_text
        target -= 1

    vim.current.buffer[line+count] = indentation + text[column:]


def dump_buffer():
    vimline, vimcolumn = vim.current.window.cursor

    log.debug('--+---------------')
    log.debug('current_line: %s', vimline-1)
    log.debug('current_column: %s', vimcolumn)

    line_nr = 0
    for line in vim.current.buffer:
        column = 0
        header = []
        text = []
        header.append("%-2s|" % str(line_nr))
        text.append("%-2s|" % str(line_nr))
        for char in line:
            header.append("%-2s" % str(column))
            text.append("%-2s" % char)
            column += 1
        line_nr += 1

        log.debug(' '.join(header))
        log.debug(' '.join(text))
        log.debug('--+---------------')

def _insert_at(position, text):
    line = position[0] - 1
    column = position[1]

    vim.current.buffer[line] = \
        vim.current.buffer[line][:column] + \
        text + \
        vim.current.buffer[line][column:]


def _delete_at(position, amount):
    cursor_before = _get_cursor()
    vim.current.buffer[position[0] - 1] = \
        vim.current.buffer[position[0] - 1][:position[1]] + \
        vim.current.buffer[position[0] - 1][position[1] + amount:]
    cursor_after = _get_cursor()

    if cursor_before == cursor_after:
        if position[0] == cursor_after[0]:
            if position[1] < cursor_after[1]:
                _move_cursor_relative(0, -amount)
                return True
    else:
        return True

    return False


def _move_cursor_relative(line, column):
    vim.current.window.cursor = (
        vim.current.window.cursor[0]+line,
        vim.current.window.cursor[1]+column
    )


def _get_cursor():
    return (
        vim.current.window.cursor[0],
        vim.current.window.cursor[1],
    )


def _set_cursor(*cursor):
    vim.current.window.cursor = cursor


def _escape_open_pair(pair):
    # need escape [ for searchpairpos since it'll be treated as regexp symbol
    if pair == "[":
        return "\\["
    return pair


enclosing_strategies = []
register_finder(_match_semicolon)
register_finder(_match_long_identifier)
register_finder(_match_enclosing_brace)
register_finder(_match_argument)
register_finder(_match_stopper)
register_finder(_match_end_of_code_block)
register_finder(_match_enclosing_quote)
register_finder(_match_end_of_line)
