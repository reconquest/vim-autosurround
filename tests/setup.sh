tests:clone vendor .

tests:make-tmp-dir bundle/autosurround

tests:clone pythonx bundle/autosurround
tests:clone plugin bundle/autosurround

import github.com/reconquest/vim-tests

vim-tests:end-silent "$_vim_session"

vim-tests:start "$_vim_session" <<VIMRC
syn on
set rtp+=$(vim-tests:get-rtp "bundle")

inoremap ( (<C-R>=AutoSurround(")")?'':''<CR>
inoremap { {<C-R>=AutoSurround("}")?'':''<CR>
set ft=sh

" workaround for incorrect syntax grouping by default, linked to Constant
hi! link String NONE
VIMRC
