Plugin will automatically add enclosing `)` (or any other) at appropriate place to be.

![gif](https://cloud.githubusercontent.com/assets/674812/10417889/f530e936-703a-11e5-8f77-2b7f6fe23191.gif)

Currently, following cases are supported:

* adding pair after call-like construction:
  ```
  |something()        type: test( ->
  test(|something())
  ```

* adding pair after string:
  ```
  |"blah"       type: test( ->
  test(|"blah")
  ```

* adding pair after argument:
  ```
  something(|arg1, arg2)        type: test( ->
  something(test(|arg1), arg2)
  ```

  ```
  something(arg1, |arg2)        type: test( ->
  something(arg1, test(arg2))
  ```

* adding pairs in conditionals:
  ```
  if |blah != nil       type test( ->
  if test(blah) != nil
  ```

* autocorrection:
  ```
  something(|arg1, arg2)        type: test( ->
  something(test(|arg1), arg2)  move cursor after last ) and type ) ->
  something(test(arg1), arg2)|
  something(test(arg1, arg2))|
  ```

# Installation & Usage

```viml
Plug 'vim-autosurround'
```

Plugin provides only python API.

# Extension

Plugin provides API, which can be used to extend surround logic:

* `index = autosurround.register_finder(callback)`, `callback` is a function
  of one argument `cursor`, which is `vim.current.window.cursor`.

  `callback` should return tuple `(line, column)` with position, which will be
  used for inserting pair character or `None`, if `callback` is not able to
  find position.

  `index` can be used for `unregister_finder(index)`.

* `autosurround.unregister_finder(index)` will remove previously added
  callback.
