vim-tests:type "$_vim_session" \
    'ia b' 'enter' "escape" \
    'ggi' 'pig(' "escape" \
    'A' ')' 'escape'

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
pig(a b)
EXPECTED
