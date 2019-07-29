vim-tests:type "$_vim_session" \
    "ia" "enter" "b" "enter" "c" "enter" "escape" \
    "gg" "C-v" "2j" "I("

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
(a
(b
(c
EXPECTED
