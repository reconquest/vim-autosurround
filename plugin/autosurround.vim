py import autosurround

fun! AutoSurround(pair)
    return pyeval(printf('autosurround.surround("%s")', a:pair))
endfun
