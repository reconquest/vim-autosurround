vim-tests:type "$_vim_session" 'iblah(somevar)' "escape"
vim-tests:type "$_vim_session" '^lllla' 'ttt{' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(ttt{somevar})
EXPECTED
