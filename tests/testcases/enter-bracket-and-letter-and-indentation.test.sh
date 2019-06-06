vim-tests:type "$_vim_session" \
    "i" \
    "tab" "{" "x" "escape" "i" "enter" \
    "|" \
    "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
	{
		|x}
EXPECTED
