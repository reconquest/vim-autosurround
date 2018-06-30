vim-tests:type "$_vim_session" \
    'i' 'a = b - 1' 'escape' \
    'F' 'b' 'i' 'int(' 'escape' \
    'A' ')'

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
a = int(b - 1)
EXPECTED
