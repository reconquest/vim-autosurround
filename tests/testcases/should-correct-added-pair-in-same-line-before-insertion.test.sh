vim-tests:type "$_vim_session" \
    'iblah(somevar, x)' "escape" \
    '^lllla' 'pig(' "escape" \
    'llllli' '), ' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(pig(some), var, x)
EXPECTED
