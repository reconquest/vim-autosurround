vim-tests:type "$_vim_session" 'imap[string]interface{}{"x": 1}' "escape"
vim-tests:type "$_vim_session" 'I' 'test(' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
test(map[string]interface{}{"x": 1})
EXPECTED
