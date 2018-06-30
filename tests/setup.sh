tests:clone vendor .
tests:clone pythonx .
tests:clone plugin .
tests:clone autosurround.vimrc .

vim-tests:start "$_vim_session" < autosurround.vimrc
