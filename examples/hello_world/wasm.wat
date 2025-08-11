(module
  (import "env" "print" (func $print (param i32)))
  (memory 1)
  (data (i32.const 0) "Hola Mundo")
  (func (export "main")
        (call $print (i32.const 0)))
)
