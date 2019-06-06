tests:clone vendor .
tests:clone pythonx .
tests:clone plugin .
tests:clone autosurround.vimrc .

vim-tests:start "$_vim_session" < autosurround.vimrc

vim-tests:type "$_vim_session" ":py autosurround.enable_debug_log()" "enter"

:gif-next-id() {
    local last_id=$(cd $_gifs_dir && ls -t | head -n1 | cut -d. -f1)
    if [[ ! "$last_id" ]]; then
        echo $_gifs_dir/1
    fi
    echo $_gifs_dir/$((last_id + 1))
}

record-terminal -n "$(:gif-next-id)" -s "$_vim_session" tmux attach -t "$_vim_session" &
_gif_record=$!

sleep 1

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

    vim-tests:type "$_vim_session" "escape" "escape" "ggDG"
    rm -rf chunk*
    cp /dev/null /tmp/autosurround.log
}
