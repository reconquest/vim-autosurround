:testcase <<CASE
ia"b"c
@
a"b"c
CASE

:testcase <<CASE
i"x""y
@
"x""y"
CASE

:testcase <<CASE
i"x" "y"
@
"x" "y"
CASE

:testcase <<CASE
i"x" "y"
escape
Fxla
space
z"v
@
"x" z"v" "y"
CASE

:testcase <<CASE
i"x" "y"
escape
Fxaz"|
@
"xz"| "y"
CASE

:testcase <<CASE
i"xz" "y"
escape
Fxa"|"
@
"x"|"z" "y"
CASE

:testcase <<CASE
i
if [[ x ]]; then
escape
0fxs
"$"
@
if [[ "$" ]]; then
CASE

:testcase <<CASE
i
if [[x]]; then
escape
0fxs
"$"
@
if [["$"]]; then
CASE
