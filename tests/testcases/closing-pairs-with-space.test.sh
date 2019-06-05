vim-tests:type "$_vim_session" \
    "i" \
    "f{" "enter" "tab" "a[b.c] = d" "enter" "escape" \
    "0kf]" "i(x" "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
f{
	a[b.c(x)] = d
}
EXPECTED
