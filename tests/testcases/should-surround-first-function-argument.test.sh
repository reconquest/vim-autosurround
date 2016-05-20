vim-tests:type "$_vim_session" 'iblah(abc, somevar)' "escape"
vim-tests:type "$_vim_session" '^lllla' 'test(' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(test(abc), somevar)
EXPECTED
