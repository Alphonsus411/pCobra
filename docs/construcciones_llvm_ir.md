# Mapeo de construcciones Cobra a LLVM IR

Este documento inventaria las construcciones actuales del lenguaje Cobra y propone una representación aproximada en LLVM IR. Además, se incluyen diagramas de flujo y ejemplos de código intermedio.

## Tabla de construcciones

| Construcción Cobra | Descripción | Representación en LLVM IR |
| --- | --- | --- |
| **Asignación** | `x = 5` | `%x = alloca i32`<br>`store i32 5, ptr %x` |
| **Función** | `func sumar(a, b):` | `define i32 @sumar(i32 %a, i32 %b)` |
| **Clase** | `clase Persona:` | `%struct.Persona = type { ... }` |
| **Bucle mientras** | `mientras cond:` | `br label %cond` + `br i1 %cond, label %body, label %end` |
| **Bucle para** | `para i en rango(0, n):` | Ciclo basado en contadores con `phi` y `br` |
| **Condicional** | `si cond:` | `br i1 %cond, label %then, label %else` |
| **Importación** | `import "mod"` | Llamada a rutinas de carga en tiempo de enlace |
| **Usar** | `usar "lib"` | Similar a importación, manejado por el runtime |
| **Macro** | `macro nombre { ... }` | Expansión en tiempo de compilación, sin IR directo |
| **Impresión** | `imprimir(x)` | `call void @imprimir(i32 %x)` |
| **Retorno** | `retorno x` | `ret i32 %x` |
| **Hilo** | `hilo tarea()` | `call void @crear_hilo(ptr @tarea)` |
| **Llamada** | `f(x)` | `call i32 @f(i32 %x)` |
| **Switch** | `switch valor:` | `switch i32 %valor, label %default [ ... ]` |
| **try/catch** | `try: ... catch e:` | `invoke`/`landingpad` para manejo de excepciones |
| **Expresiones aritméticas** | `a + b` | `add i32 %a, %b` (o `fadd` para flotantes) |
| **Holobit** | `holobit([1,2])` | `<2 x double> <1.0, 2.0>` u estructura específica |

## Diagramas de flujo

### Condicional `si/sino`

```{uml}
@startuml
start
if (condición) then (sí)
  :bloque si;
else (no)
  :bloque sino;
endif
stop
@enduml
```

### Bucle `mientras`

```{uml}
@startuml
start
while (condición) is (verdadero)
  :cuerpo;
endwhile (falso)
stop
@enduml
```

## Ejemplo de código intermedio

### Fuente Cobra

```cobra
mientras i < 4:
    imprimir(i)
    i = i + 1
fin
```

### LLVM IR aproximado

```llvm
define void @ejemplo() {
entry:
    %i = alloca i32, align 4
    store i32 0, ptr %i
    br label %cond

cond:
    %tmp = load i32, ptr %i
    %cmp = icmp slt i32 %tmp, 4
    br i1 %cmp, label %body, label %end

body:
    %tmp2 = load i32, ptr %i
    call void @imprimir(i32 %tmp2)
    %tmp3 = add i32 %tmp, 1
    store i32 %tmp3, ptr %i
    br label %cond

end:
    ret void
}
```
