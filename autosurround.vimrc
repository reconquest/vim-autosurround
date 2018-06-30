set nocompatible

syn on
set rtp+=.
source plugin/autosurround.vim

set ft=python

" workaround for incorrect syntax grouping by default, linked to Constant
hi! link String NONE
