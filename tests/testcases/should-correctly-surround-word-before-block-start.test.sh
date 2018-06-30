vim-tests:type "$_vim_session" 'ix {' "escape"
vim-tests:type "$_vim_session" '^iblah(' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(x) {
EXPECTED
