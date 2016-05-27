vim-tests:type "$_vim_session" 'ia()' "escape"
vim-tests:type "$_vim_session" ':mess' "enter"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:fail

tests:assert-no-diff "result" <<EXPECTED
a
EXPECTED
