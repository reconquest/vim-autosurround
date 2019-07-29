vim-tests:type "$_vim_session" \
    "ifirst(second())" "escape" \
    "2F(" 'a"abc",'

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
first("abc",second())
EXPECTED
