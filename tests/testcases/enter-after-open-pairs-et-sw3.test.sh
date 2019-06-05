vim-tests:type "$_vim_session" ":set et" "enter"
vim-tests:type "$_vim_session" ":set sw=3" "enter"

vim-tests:type "$_vim_session" \
    "i" \
    "{"  "enter" "|" "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
{
   |
}
EXPECTED
