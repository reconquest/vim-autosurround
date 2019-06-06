vim-tests:type "$_vim_session" \
    "i" \
    "a b c<CR>" "escape" \
    "0fca(" "bspace" "|"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
a b c|<CR>
EXPECTED
