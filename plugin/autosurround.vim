py import autosurround

fun! AutoSurround(pair)
    return pyeval(printf('autosurround.surround("%s")', a:pair))
endfun

fun! AutoSurroundInitMappings()
    inoremap <silent> <buffer> )
        \ <C-R>=pyeval("autosurround.correct_inserted_pair('(', ')')")
            \ ? ')'
            \ : (exists('*g:MatchemMatchEnd') ? MatchemMatchEnd(')') : ')')<CR>
endfun!

augroup autosurround
    au!
    au CursorMovedI * py autosurround.clean_current_pairs()
    au BufEnter,FileType * call AutoSurroundInitMappings()
augroup END

