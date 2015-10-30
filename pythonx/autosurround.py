# coding=utf8

import vim
import re
from contextlib import contextmanager


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

    return True


def find_enclosure(cursor):
    for strategy in reversed(enclosing_strategies):
        if strategy is None:
            continue

        pos = strategy(cursor)
        if pos is not None:
            return pos


def _match_enclosing_brace(cursor):
    line = vim.current.buffer[cursor[0]-1][cursor[1]:]
    match = re.match(r'^(\[[.\w_\[\]-]+|[.\w_-]*)[([{]', line)
    if not match:
        return

    with _restore_cursor():
        vim.command('normal! {}%'.format(
            (str(len(match.group(1))) + 'l') if match.group(1) != '' else ''
        ))
        return vim.current.window.cursor


def _match_enclosing_quote(cursor):
    line = vim.current.buffer[cursor[0]-1][cursor[1]:]
    if not re.match(r'^["\'`]', line):
        return

    quote = line[0].replace('"', '\\"')

    with _restore_cursor():
        while int(vim.eval('search("{}", "W")'.format(quote))) > 0:
            cursor = vim.current.window.cursor
            match_pos = cursor

            if len(vim.current.buffer[cursor[0]-1]) == cursor[1]+1:
                vim.command('normal! +')
            else:
                vim.command('normal! l')

            still_inside_string = False
            for syn_id in vim.eval('synstack(line("."), col("."))'):
                syn_name = vim.eval(
                    'synIDattr(synIDtrans({}), "name")'.format(syn_id)
                )
                if syn_name.lower() == 'string':
                    still_inside_string = True
                    break

            if not still_inside_string:
                vim.current.window.cursor = match_pos
                return vim.current.window.cursor


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


enclosing_strategies = []
register_finder(_match_enclosing_quote)
register_finder(_match_enclosing_brace)
