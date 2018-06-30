py import vim, autosurround

fun! AutoSurroundInitMappings()
    inoremap <silent> <buffer> ( <C-\><C-O>:py autosurround.surround('(', ')')<CR>

    inoremap <silent> <buffer> ) <C-\><C-O>:py autosurround.correct_pair('(', ')')<CR>
endfun!

augroup autosurround
    au!
    au CursorMovedI * py autosurround.clean_current_pairs()
    au BufEnter,FileType * call AutoSurroundInitMappings()
augroup END

