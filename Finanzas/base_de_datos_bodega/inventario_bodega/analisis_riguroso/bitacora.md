# Bitácora de trabajo del 09/09/2022

1. En primer lugar, se generó un inventario el Viernes 02/09/2022 (Inventario A), el que estaba malo. Esto, ya que poseía Códigos,
Fechas de Vencimiento y Lotes mal digitados. Este inventario fue subido al sistema informático.
2. De este inventario erróneo, se generaron movimientos de entrada/salida. Debido a lo anterior, estuvo la predicción
de que iban a haber movimientos de productos que contenían información errónea.
3. Debido a lo anterior, se volvió a digitar el contenido del inventario inicial, para generar un inventario "digitado correctamente" (Inventario B).
4. La tarea que era necesaria hacer, era asociar la información de este nuevo inventario a los movimientos registrados.
5. Además, generar un inventario actual nuevo (calcular cantidades actuales, teniendo en cuenta los movimientos que se registraron)

- El modo de trabajo fué: 
1. Tomar la planilla del Max, con toda la información corregida, y restarle los movimientos. En este caso, habían 2 posibles casos:
- Que el elemento efectivamente se restara/sumara, indicando que el código/información entre el inventario A y el inventario B era igual.
- Que el elemento se restara, y quedara negativo. Esto indicaba que ese artículo que tuvo movimientos, estaba ausente en la planilla del Max.
- Ahora, creo que hay un caso que no se considero, y es cuando un artículo tuvo un ingreso, y no existía en la planilla inicial. En ese caso, 
el elemento simplemente aparecería como +.

2. Por lo tanto, para identificar estos elementos que están ausentes en la planilla del Max, es necesario hacer un .isin me parece. 