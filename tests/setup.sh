tests:clone vendor .
tests:clone pythonx .
tests:clone plugin .
tests:clone autosurround.vimrc .

vim-tests:start "$_vim_session" < autosurround.vimrc

vim-tests:type "$_vim_session" ":py autosurround.enable_debug_log()" "enter"

:testcase() {
    cat > table
    csplit \
        --prefix=chunk \
        --suppress-matched table \
        '/^@$/' '{*}' >/dev/null
    while read cmd; do
        vim-tests:type "$_vim_session" "$cmd"
    done < chunk00
    tests:eval tmux:cat-screen "$_vim_session" <&-

    vim-tests:write-file "$_vim_session" "result"
    tests:assert-no-diff "result" < chunk01

    vim-tests:type "$_vim_session" "escape" "escape" "ggVGdd" "escape"
    rm -rf chunk*
    cp /dev/null /tmp/autosurround.log
}
