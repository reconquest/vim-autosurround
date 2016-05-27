vim-tests:type "$_vim_session" \
    'iblah()' 'enter' '}' "escape" \
    'gglllla' 'pig()' "escape" \
    'xxx' 'A' '())' 'escape'

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(pig())
}
EXPECTED
