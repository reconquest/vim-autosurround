vim-tests:type "$_vim_session" \
    "i" \
    "files[header.Name] = contents" "escape" \
    "0f]" "i]|" "escape"

tests:eval tmux:cat-screen "$_vim_session"

vim-tests:write-file "$_vim_session" "result"

tests:assert-no-diff "result" <<EXPECTED
files[header.Name]| = contents
EXPECTED
