# coding=utf8

import vim
import re
from contextlib import contextmanager

_current_pairs = {}


def surround(pair):
    end_pos = find_enclosure(vim.current.window.cursor)
    if not end_pos:
        return False

    cursor = vim.current.window.cursor
    begin = vim.current.buffer[cursor[0] - 1][cursor[1] - 1]

    # breaks undo and keep cursor at place
    # vim.command('let &undolevels = &undolevels')
    vim.command('normal! "_X')
    vim.command('normal! i' + begin)
    vim.command('normal! l')

    with _restore_cursor():
        vim.current.window.cursor = (end_pos[0], end_pos[1])
        vim.command('normal! a' + pair)

    _current_pairs[(cursor, pair)] = (end_pos[0], end_pos[1] + 1)

    return True


def find_enclosure(cursor):
    for strategy in reversed(enclosing_strategies):
        if strategy is None:
            continue

        pos = strategy(cursor)
        if pos is not None:
            return pos


def correct_inserted_pair(open, close):
    buffer = vim.current.buffer

    with _restore_cursor():
        for pair in _current_pairs:
            corrected = False

            close_pair_pos = _current_pairs[pair]

            if len(buffer[close_pair_pos[0] - 1]) <= close_pair_pos[1]:
                continue

            if buffer[close_pair_pos[0] - 1][close_pair_pos[1]] != close:
                continue

            buffer[close_pair_pos[0] - 1] = \
                buffer[close_pair_pos[0] - 1][:close_pair_pos[1]] + \
                buffer[close_pair_pos[0] - 1][close_pair_pos[1] + 1:]

            try:
                open_pair_pos = vim.eval(
                    'searchpairpos("{}", "", "{}", "nb")'.format(
                        open, close,
                    )
                )

                open_pair_pos = (int(open_pair_pos[0]), int(open_pair_pos[1]))

                if open_pair_pos == (0, 0):
                    return

                open_pair = (open_pair_pos, close)

                if open_pair not in _current_pairs:
                    return

                if _current_pairs[open_pair] == close_pair_pos:
                    corrected = True
            finally:
                if not corrected:
                    buffer[close_pair_pos[0] - 1] = \
                        buffer[close_pair_pos[0] - 1][:close_pair_pos[1]] + \
                        close + \
                        buffer[close_pair_pos[0] - 1][close_pair_pos[1]:]
                else:
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


def _match_enclosing_quote(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r"(['\"`]).*", line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    if not _is_cursor_in_string((cursor[0], cursor[1] + 1)):
        return

    old_cursor = vim.current.window.cursor

    with _restore_selection_register():
        with _restore_cursor():
            vim.command("normal! va{}\033".format(match.group(1)))
            if vim.current.window.cursor > old_cursor:
                return vim.current.window.cursor


def _match_long_identifier(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^([.\w_\[\]-]+)\s', line)
    if not match:
        return

    if match.group(1).count(']') != match.group(1).count('['):
        return

    if _is_cursor_in_string(cursor):
        return

    return (cursor[0], cursor[1] + len(match.group(1)) - 1)


def _match_enclosing_brace(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^(\[[.\w_\[\]-]+|[.\w_-]*)[([{]', line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    with _restore_cursor():
        vim.command('normal! {}%'.format(
            (str(len(match.group(1))) + 'l') if match.group(1) != '' else ''
        ))
        return vim.current.window.cursor


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
            return (cursor[0], len(matches.group(1)) - 1)


def _match_argument(cursor):
    if _is_cursor_in_string(cursor):
        return

    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]

    matches = re.match(r'([\w.]+)[,)\]]', line)
    if not matches:
        return

    return (cursor[0], cursor[1] + len(matches.group(1)) - 1)


def _match_semicolon(cursor):
    line = vim.current.buffer[cursor[0] - 1][cursor[1]:]
    match = re.match(r'^(.*);', line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    return (cursor[0], cursor[1] + len(match.group(1)) - 1)


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
    synstack = vim.eval('synstack({}, {})'.format(
        cursor[0],
        cursor[1]
    ))

    for syn_id in synstack:
        syn_name = vim.eval(
            'synIDattr(synIDtrans({}), "name")'.format(syn_id)
        )
        if syn_name.lower() == 'string':
            return True
            break

    return False


enclosing_strategies = []
register_finder(_match_enclosing_quote)
register_finder(_match_argument)
register_finder(_match_end_of_code_block)
register_finder(_match_enclosing_brace)
register_finder(_match_long_identifier)
register_finder(_match_semicolon)
