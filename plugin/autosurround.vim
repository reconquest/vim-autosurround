py import autosurround

fun! AutoSurround(pair)
    call pyeval(printf('autosurround.surround("%s")', a:pair))

    return ''
endfun

fun! AutoSurroundCorrect(open, close)
    call pyeval(printf(
        \ 'autosurround.correct_inserted_pair("%s", "%s")',
        \ a:open, a:close))

    return a:close
endfun

fun! AutoSurroundInitMappings()
    inoremap <silent> <buffer> ( (<C-R>=AutoSurround(')')<CR>

    inoremap <silent> <buffer> ) <C-R>=AutoSurroundCorrect('(', ')')<CR>
endfun!

augroup autosurround
    au!
    au CursorMovedI * py autosurround.clean_current_pairs()
    au BufEnter,FileType * call AutoSurroundInitMappings()
augroup END

