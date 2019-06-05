vim-tests:type "$_vim_session" \
    'i' 'fn("a", "b")' "escape" \
    '0f(a[' "bspace"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
fn("a", "b")
EXPECTED
