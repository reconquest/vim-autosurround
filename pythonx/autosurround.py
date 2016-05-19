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
    begin = vim.current.buffer[cursor[0]-1][cursor[1]-1]

    # breaks undo and keep cursor at place
    vim.command('let &undolevels = &undolevels')
    vim.command('normal! "_X')
    vim.command('normal! i' + begin)
    vim.command('normal! l')

    with _restore_cursor():
        vim.current.window.cursor = (end_pos[0], end_pos[1])
        vim.command('normal! a' + pair)

    _current_pairs[(cursor, pair)] = (end_pos[0], end_pos[1]+1)

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

    open_pair_pos = vim.eval(
        'searchpairpos("{}", "", "{}", "nb")'.format(
            open, close,
        )
    )

    if not open_pair_pos:
        return

    open_pair_pos = (int(open_pair_pos[0]), int(open_pair_pos[1]))

    if open_pair_pos == (0, 0):
        return

    corrected = False
    cursor = vim.current.window.cursor
    if (buffer[open_pair_pos[0]-1][open_pair_pos[1]-1]) == open:
        open_pair = ((open_pair_pos[0], open_pair_pos[1]), close)
        if open_pair not in _current_pairs:
            return

        cursor = vim.current.window.cursor
        close_pair_pos = _current_pairs[open_pair]
        if close_pair_pos != (cursor[0], cursor[1]):
            corrected = True
            buffer[cursor[0]-1] = \
                buffer[cursor[0]-1][:close_pair_pos[1]] + \
                buffer[cursor[0]-1][close_pair_pos[1]+1:]
            del _current_pairs[open_pair]

    return corrected


def clean_current_pairs():
    global _current_pairs

    cursor = vim.current.window.cursor
    cursor = (cursor[0], cursor[1]+1)

    kept_pairs = {}
    for open_pair in _current_pairs:
        open_pair_pos = open_pair[0]
        close_pair_pos = _current_pairs[open_pair]
        if open_pair_pos <= cursor <= close_pair_pos:
            kept_pairs[open_pair] = close_pair_pos

    _current_pairs = kept_pairs


def _match_enclosing_quote(cursor):
    line = vim.current.buffer[cursor[0]-1][cursor[1]:]
    match = re.match(r"(['\"`]).*", line)
    if not match:
        return

    if _is_cursor_in_string(cursor):
        return

    if not _is_cursor_in_string((cursor[0], cursor[1]+1)):
        return

    with _restore_selection_register():
        with _restore_cursor():
            vim.command("normal! va{}\033".format(match.group(1)))
            return vim.current.window.cursor


def _match_enclosing_brace(cursor):
    line = vim.current.buffer[cursor[0]-1][cursor[1]:]
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

    if len(vim.current.buffer[cursor[0]-1]) == cursor[1]:
        return

    if vim.current.buffer[cursor[0]-1][-1] in ')]}{[(':
        return

    if len(vim.current.buffer) > cursor[0]:
        stripped_line = vim.current.buffer[cursor[0]].strip()
        if stripped_line == '}' or stripped_line == '':
            return (cursor[0], len(vim.current.buffer[cursor[0]-1]))


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
register_finder(_match_end_of_code_block)
register_finder(_match_enclosing_brace)
register_finder(_match_enclosing_quote)
