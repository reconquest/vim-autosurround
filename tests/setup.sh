tests:clone vendor .
tests:clone pythonx .
tests:clone plugin .
tests:clone autosurround.vimrc .

vim-tests:start "$_vim_session" < autosurround.vimrc
vim-tests:type "$_vim_session" ":py autosurround.enable_debug_log()" "enter"
