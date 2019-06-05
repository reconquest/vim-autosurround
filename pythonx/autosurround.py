# coding=utf8

import vim
import re
from contextlib import contextmanager

_current_pairs = {}


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
                    open_pair,
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
                    move_cursor_relative(0, 1)

                debug_cursor()
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

        if not re.match(r'^[)}"\]]+$', next):
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


def remove_pair(open_pair, close_pair):
    pair_pos = vim.Function('searchpairpos')(
        open_pair,
        "",
        close_pair,
        "n",
    )

    if pair_pos[0] == 0 and pair_pos[0] == 0:
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
        matches = re.match(r'^[)}"\]]+$', line[cursor[1]:])
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

_debug = False
def debug_cursor():
    global _debug
    if not _debug:
        return
    vimline, vimcolumn = vim.current.window.cursor
    column = 0
    header = []
    text = []
    for char in vim.current.buffer[vimline-1]:
        header.append("%-2s" % str(column))
        text.append("%-2s" % char)
        column += 1
    print('------------------')
    print('current_column: ', vimcolumn)
    print(' '.join(header))
    print(' '.join(text))
    print('------------------')

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
                move_cursor_relative(0, -amount)
                return True
    else:
        return True

    return False


def move_cursor_relative(line, column):
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


enclosing_strategies = []
register_finder(_match_semicolon)
register_finder(_match_long_identifier)
register_finder(_match_enclosing_brace)
register_finder(_match_argument)
register_finder(_match_end_of_code_block)
register_finder(_match_enclosing_quote)
register_finder(_match_end_of_line)
