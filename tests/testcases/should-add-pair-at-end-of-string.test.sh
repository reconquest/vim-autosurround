vim-tests:type "$_vim_session" 'iabc(def(xxx' "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
abc(def(xxx))
EXPECTED
