vim-tests:type "$_vim_session" \
    'i' 'blah(abc, somevar)' 'escape' \
    '^' '4l' 'a' 'test(' 'escape'

vim-tests:type "$_vim_session" \
    'o' 'enter' '{' "enter" "blah(abc, somevar)" "escape" \
    '^' '4l' 'a' 'test(' 'escape'

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
blah(test(abc), somevar)

{
	blah(test(abc), somevar)
}
EXPECTED
