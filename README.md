Plugin will automatically add enclosing `)` or `}` (or any other) at appropriate place to be.

![gif](https://cloud.githubusercontent.com/assets/674812/10417889/f530e936-703a-11e5-8f77-2b7f6fe23191.gif)

Currently, two cases are supported:

* adding pair after call-like construction:
  ```
  |something()        type: test( ->
  test(|something())
  ```

* adding pair after string:
  ```
  |"blah"       type: test( ->
  test("blah")
  ```

Undo will remove added pair and leaving cursor in-place:

```
|(blah)        type: test(  ->
test(|(blah))  type: <Esc>u ->
test(|(blah)
```

# Installation & Usage

Plugin provides only one function, named `AutoSurround(pair)`. `pair` is
character, which will be inserted at position, determined by internal
algorithms, described above, or [user-registered functions](#extension).

```viml
Plug 'vim-autosurround'
    inoremap  ( (<C-O>AutoSurround(")")<CR>
```

In case of using `matchem` or similar surrounding plugins things are going to
be *little* bit harder:

```viml
augroup run_after_plug_end
    au!

call plug#begin('~/.vim/bundle')

" ...

Plug 'vim-autosurround'
    au User _OverwriteMatchemMappings
        \ autocmd VimEnter,BufEnter,FileType *
            \ inoremap <buffer> ( (<C-R>=AutoSurround(")")?'':g:MatchemMatchStart()<CR>

    au User _VimrcRunAfterPlugEnd doautocmd User _OverwriteMatchemMappings

    doautocmd User _OverwriteMatchemMappings

" ...

augroup end

call plug#end()

au VimEnter * doautocmd User _VimrcRunAfterPlugEnd
au VimEnter * au! run_after_plug_end
```

# Extension

Plugin provides API, which can be used to extend surround logic:

* `index` = `autosurround.register_finder(callback)`, `callback` is a function
  of one argument `cursor`, which is `vim.current.window.cursor`; `callback`
  should return tuple `(line, column)` with position, which will be used for
  inserting pair character or `None`, if `callback` is not able to find
  position.

  `index` can be used for `unregister_finder(index)`

* `autosurround.unregister_finder(index)` will remove previously added
  callback.
