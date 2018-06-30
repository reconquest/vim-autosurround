set nocompatible

syn on
set rtp+=.
source plugin/autosurround.vim

set ft=python
set backspace=2

" workaround for incorrect syntax grouping by default, linked to Constant
hi! link String NONE
