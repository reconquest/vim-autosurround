vim-tests:type "$_vim_session" \
    "alocal abc=def" "enter" "escape" \
    "k^f=a" "test(" "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
local abc=test(def)

EXPECTED
