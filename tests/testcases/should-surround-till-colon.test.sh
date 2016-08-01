vim-tests:type "$_vim_session" 'icase true:' "enter" "escape"
vim-tests:type "$_vim_session" 'k^lllla' 'test(' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
case test(true):
EXPECTED
