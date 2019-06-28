py import vim, autosurround

let g:autosurround_enquote_filetypes_exclude = get(
        \ g:, 'autosurround_enquote_filetypes_exclude', ['markdown', ''])

fun! AutoSurroundInitMappings()
    if index(g:autosurround_enquote_filetypes_exclude, &ft) < 0
        inoremap <silent> <buffer> " <C-\><C-O>:py autosurround.enquote('"')<CR>
        inoremap <silent> <buffer> ' <C-\><C-O>:py autosurround.enquote("'")<CR>
    endif

    inoremap <silent> <buffer> ( <C-\><C-O>:py autosurround.surround('(', ')')<CR>
    inoremap <silent> <buffer> ) <C-\><C-O>:py autosurround.correct_pair('(', ')')<CR>

    inoremap <silent> <buffer> [ <C-\><C-O>:py autosurround.surround('[', ']')<CR>
    inoremap <silent> <buffer> ] <C-\><C-O>:py autosurround.correct_pair('[', ']')<CR>

    inoremap <silent> <buffer> { <C-\><C-O>:py autosurround.surround('{', '}')<CR>
    inoremap <silent> <buffer> } <C-\><C-O>:py autosurround.correct_pair('{', '}')<CR>

    inoremap <silent> <buffer> <backspace> <C-\><C-O>:py autosurround.remove_pair()<CR><C-H>
    inoremap <silent> <buffer> <CR> <C-\><C-O>:py autosurround.insert_new_line()<CR>
endfun!

augroup autosurround
    au!
    au CursorMovedI * py autosurround.clean_current_pairs()
    au BufEnter,FileType * call AutoSurroundInitMappings()
augroup END

