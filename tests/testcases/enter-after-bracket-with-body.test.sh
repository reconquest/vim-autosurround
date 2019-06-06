vim-tests:type "$_vim_session" \
    "i" \
    "fn(" "enter" \
    "a int," \
    "escape" "kA" "enter" \
    "|" \
    "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
fn(
	|
	a int,
)
EXPECTED
