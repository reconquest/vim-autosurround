python3 import vim, autosurround

let g:autosurround_enquote_filetypes_exclude = get(
        \ g:, 'autosurround_enquote_filetypes_exclude', ['markdown', ''])

fun! AutoSurroundInitMappings()
    if index(g:autosurround_enquote_filetypes_exclude, &ft) < 0
        inoremap <silent> <buffer> " <C-\><C-O>:python3 autosurround.enquote('"')<CR>
        inoremap <silent> <buffer> ' <C-\><C-O>:python3 autosurround.enquote("'")<CR>
    endif

    inoremap <silent> <buffer> ( <C-\><C-O>:python3 autosurround.surround('(', ')')<CR>
    inoremap <silent> <buffer> ) <C-\><C-O>:python3 autosurround.correct_pair('(', ')')<CR>

    inoremap <silent> <buffer> [ <C-\><C-O>:python3 autosurround.surround('[', ']')<CR>
    inoremap <silent> <buffer> ] <C-\><C-O>:python3 autosurround.correct_pair('[', ']')<CR>

    inoremap <silent> <buffer> { <C-\><C-O>:python3 autosurround.surround('{', '}')<CR>
    inoremap <silent> <buffer> } <C-\><C-O>:python3 autosurround.correct_pair('{', '}')<CR>

    inoremap <silent> <buffer> <backspace> <C-\><C-O>:python3 autosurround.remove_pair()<CR><C-H>
endfun!

augroup autosurround
    au!
    au BufEnter,FileType * call AutoSurroundInitMappings()
augroup END

