# Análisis Comparativo: RGB vs. HSV

*Trabajo Práctico Nº2 — Visión Artificial — Licenciatura en Automatización y Control — UTN FRC*

---

## Introducción

Un espacio de color es una representación numérica del color dentro de un sistema de coordenadas. En términos de procesamiento de imágenes, no se trata solamente de "guardar colores", sino de organizar la información cromática de manera que determinadas operaciones resulten más convenientes: adquisición, visualización, medición, comparación, segmentación o conversión entre modelos. Por esa razón existen distintos espacios de color; cada uno reordena la misma información con diferentes ventajas operativas y computacionales.

En visión artificial, la necesidad de un espacio de color surge de un problema básico: la escena física debe transformarse en datos procesables por un algoritmo. La cámara mide radiación luminosa y la codifica en canales numéricos; luego, esos canales deben interpretarse para distinguir objetos, materiales, estados o regiones de interés. La elección del espacio de color influye directamente en la robustez del sistema, porque modifica cómo quedan representadas variaciones de tono, brillo, sombras y reflejos dentro del dato digital.

La relación entre percepción visual y representación digital también es central. La visión humana del color es tricromática: surge de la comparación entre tres clases de conos con distinta sensibilidad espectral. Además, el color agrega capacidad de discriminación allí donde la luminancia por sí sola puede resultar insuficiente. En consecuencia, muchos espacios de color intentan aproximarse, en distinto grado, a atributos perceptuales como tono, saturación y brillo, para facilitar tareas de análisis visual automáticas.

---

## Espacio de color RGB

El modelo RGB representa cada píxel mediante tres componentes: rojo, verde y azul. En una formulación matricial, una imagen color puede modelarse como:

$$I(x,y) = [R(x,y), G(x,y), B(x,y)]^\top$$

O, en términos de almacenamiento, como un arreglo de dimensiones $m \times n \times 3$. En implementaciones típicas de 8 bits por canal, cada componente toma valores enteros entre 0 y 255; en punto flotante, valores reales entre 0 y 1. Desde la perspectiva conceptual el modelo es RGB, aunque en OpenCV la codificación por defecto de imágenes de color suele almacenarse como BGR (con el orden de bytes invertido).

RGB es un modelo aditivo. Esto significa que los colores se generan por superposición de intensidades luminosas de tres primarias. En el plano físico y tecnológico, este modelo es natural para pantallas, sensores y gran parte del hardware de adquisición y visualización. La combinación aditiva de esas primarias compone la percepción final del color. En ese sentido, RGB es el formato más directo para capturar y mostrar imágenes.

La relación entre intensidad lumínica y color en RGB es especialmente importante para visión artificial. Los valores de canal son directamente proporcionales a la cantidad de luz que llega al sensor (*linear RGB*), y *sRGB* es el modelo donde se aplica una corrección gamma para visualización. Esta observación tiene consecuencias prácticas: cuando cambia la iluminación de la escena, cambian los valores numéricos de R, G y B, de modo que el color y la iluminación quedan fuertemente acoplados en la representación.

Desde un punto de vista ingenieril, RGB presenta ventajas claras. Es el formato nativo de adquisición de muchos sensores, evita conversiones cuando el objetivo es almacenar o visualizar, y resulta apropiado para algoritmos que explotan información radiométrica completa o aprenden directamente sobre las tres bandas originales. Sin embargo, no existe un espacio universalmente óptimo: la elección depende del color buscado y de la tarea. Por lo tanto, adoptar HSV no debe entenderse como una regla absoluta, sino como una decisión dependiente del problema.

Sin embargo, RGB exhibe limitaciones concretas cuando la tarea es segmentación cromática por umbrales. Como los colores en RGB están codificados en tres canales simultáneamente, segmentar un objeto por color resulta más difícil que en HSV. El motivo estructural es que un mismo color perceptual no ocupa una región simple y estable del cubo RGB cuando varían la intensidad, las sombras o los reflejos: una sombra tiende a reducir simultáneamente magnitudes de canal, un reflejo especular puede acercar el píxel al blanco, y las variaciones de exposición o balance de blancos desplazan el vector RGB completo. Las condiciones de iluminación, sombras, reflejos e interferencias luminosas degradan la detección cuando no se dispone de una representación más separable del color.

En síntesis, RGB es excelente como espacio de adquisición, representación y visualización, pero es menos conveniente cuando el objetivo principal es aislar clases cromáticas mediante umbrales simples y robustos. Esa desventaja no surge de una "falta de información", sino de la forma en que dicha información queda mezclada en los tres canales.

---

## Espacio de color HSV

El espacio HSV reorganiza la información cromática en tres componentes con significado más cercano a la interpretación humana: **Hue** (tono), **Saturation** (saturación) y **Value** (brillo). Este espacio corresponde mejor a la manera en que las personas experimentan el color que RGB; además, el canal de tono modela el "tipo de color", por lo que resulta especialmente útil cuando la tarea exige segmentar objetos en función de su cromaticidad.

*   **Tono (H):** Representa la posición angular sobre la rueda de color. En la formulación conceptual habitual, el tono recorre el ciclo rojo $\rightarrow$ naranja $\rightarrow$ amarillo $\rightarrow$ verde $\rightarrow$ cian $\rightarrow$ azul $\rightarrow$ magenta $\rightarrow$ rojo.
*   **Saturación (S):** Cuantifica cuánta pureza cromática tiene el color, es decir, cuánto se aleja del eje acromático; a saturación nula se obtienen tonos grises.
*   **Brillo (V):** Representa la intensidad luminosa y, en la conversión clásica desde RGB, coincide con el valor máximo entre las tres componentes originales ($V = \max(R,G,B)$). La saturación puede escribirse como $S = \Delta/V$ con $\Delta = \max - \min$ para píxeles no acromáticos.

Geométricamente, HSV suele representarse como un cilindro, un hexacono o un cono invertido, según la convención gráfica adoptada. En todos los casos la interpretación es equivalente: el tono es el ángulo, la saturación es la distancia radial al eje central y el valor es la coordenada vertical asociada al brillo. Esa geometría es útil porque hace explícita una propiedad operativa fundamental: los grises se concentran sobre el eje central, mientras que los colores saturados se disponen en la periferia. En otras palabras, HSV separa de manera más legible qué parte del dato describe "qué color es" y cuál describe "cuán brillante o cuán puro es".

Esa separación, no obstante, es solo parcial. HSV no es un espacio físicamente independiente del sensor ni de la iluminación; sigue siendo una transformación algebraica del RGB medido por la cámara y es relativo al espacio RGB subyacente. Además, cuando un píxel es acromático, el tono deja de tener significado útil: el gris no tiene tono definido. Por ello, HSV mejora la manipulabilidad de la información cromática, pero no elimina por completo la dependencia respecto del sistema de captura ni hace al problema inmune a iluminación extrema, balance de blancos o saturación del sensor.

En OpenCV, estas particularidades deben conocerse con precisión porque afectan directamente el ajuste de umbrales. La conversión estándar `COLOR_BGR2HSV` o `COLOR_RGB2HSV` usa, para imágenes de 8 bits, un rango de **H** entre 0 y 180, mientras que el modo `HSV_FULL` extiende **H** a 0–255. OpenCV divide el tono en grados por la mitad ($H_{\text{OpenCV}} = H_{\text{grados}} / 2$) para que quepa en un solo byte (0-255). Esto significa que **H** se representa en 0–179 y **S**, **V** en 0–255. Esta compresión angular de H implica además que las tonalidades cercanas al rojo queden repartidas a ambos lados del origen angular (cerca de 0 y cerca de 179) y, en la práctica, requieran dos intervalos y la suma de dos máscaras.

| Canal | Significado técnico | Interpretación geométrica | Consideración operativa en OpenCV |
| :---: | :--- | :--- | :--- |
| **H** | Tipo de color o tono dominante. | Ángulo alrededor del eje cromático. | En 8 bits estándar se maneja en 0–179; en `HSV_FULL`, en 0–255. |
| **S** | Pureza del color; mide alejamiento respecto del gris. | Radio respecto del eje acromático. | Valores bajos acercan el píxel a gris y reducen la utilidad del tono H. |
| **V** | Brillo o intensidad perceptual operativa. | Altura sobre el eje vertical. | En 8 bits se umbraliza típicamente entre 0 y 255. |

---

## Comparación estructural: RGB vs. HSV

La comparación técnica entre RGB y HSV debe partir de una premisa metodológica importante: no existe un espacio "mejor" en términos absolutos para toda tarea de visión artificial. La elección depende del color buscado y de la tarea; de forma consistente, en algunos algoritmos de segmentación avanzada RGB puede superar a HSV, mientras que en otros es a la inversa. La decisión correcta, entonces, no es universal sino contextual.

Dicho eso, cuando el problema consiste específicamente en **segmentar por color mediante umbrales**, HSV ofrece una organización más conveniente que RGB. Bajo iluminación natural variable, sombras, reflejos e interferencias, los métodos basados en HSV logran un desempeño más robusto porque permiten desacoplar mejor el atributo cromático del atributo de brillo durante la clasificación.

| Aspecto | RGB | HSV |
| :--- | :--- | :--- |
| **Organización de la información** | El color queda codificado como tres intensidades simultáneas $(R,G,B)$. | El color se reorganiza como tono, pureza y brillo $(H,S,V)$. |
| **Estabilidad ante iluminación global** | Cambios de luz modifican directamente los tres canales; el color y la iluminación quedan acoplados. | El brillo se concentra en V y el tono en H, lo que mejora la separación operativa bajo cambios moderados. |
| **Respuesta a sombras y reflejos** | Las sombras contraen el vector RGB y los reflejos pueden acercarlo al blanco; un umbral fijo se vuelve frágil. | Sombras y reflejos siguen afectando la detección, pero con frecuencia pueden absorberse mejor mediante bandas sobre S y V, manteniendo el criterio de color en H. |
| **Facilidad de segmentación por umbral** | Más difícil, porque el "mismo color" no se expresa como una región simple e intuitiva del cubo RGB. | Más directa, porque el tono se vuelve una variable explícitamente en un solo canal. |
| **Robustez al ruido en grises** | El ruido en canales modifica simultáneamente cromaticidad y brillo; en zonas oscuras o brillantes el ajuste es delicado. | No elimina el ruido, pero lo reorganiza; cerca del eje gris (baja saturación) H pierde estabilidad práctica. |
| **Sensibilidad espectral** | Depende del sensor y de sus filtros RGB. | También depende del sensor, porque HSV es una transformación de RGB; no agrega información espectral nueva. |
| **Casos de uso típicos** | Captura, almacenamiento, visualización y algoritmos de aprendizaje que seleccionan sus propias combinaciones. | Segmentación cromática, seguimiento de objetos por color, interfaces de ajuste de umbral y detección por rangos. |

Aplicado específicamente al TP, el criterio de comparación se vuelve más claro. Si la tarea consiste en detectar objetos o regiones por color con OpenCV, usando umbrales e inspección visual del resultado, el espacio más útil no es el que mejor preserva la medición cruda del sensor, sino el que transforma el problema en una decisión geométrica simple y estable. Bajo ese criterio, HSV resulta más conveniente porque permite plantear la pregunta "¿el píxel tiene este tono?" de forma casi directa, y relegar la tolerancia frente a brillo y pureza a bandas separadas sobre S y V.

---

## Justificación técnica de HSV para segmentación

La justificación formal de HSV en segmentación se basa en la estructura del operador de umbralización que efectivamente se utiliza en OpenCV. `cv2.inRange()` verifica si el valor del píxel se encuentra entre un límite inferior y otro superior de manera **inclusiva** en cada canal. Si el píxel cae dentro de la caja multidimensional definida por esos límites, la salida vale 255; en caso contrario, vale 0. El resultado es una máscara binaria de tipo `CV_8U` del mismo tamaño que la imagen de entrada.

Ese hecho permite formular el problema de segmentación cromática como una cuestión geométrica: elegir una "caja" en el espacio de color. Si esa caja se define en RGB, el algoritmo trabaja sobre tres intensidades acopladas, por lo que el rango admisible debe absorber simultáneamente cambios de tono aparente, exposición, sombras y reflejos. En consecuencia, la selección de umbrales tiende a ser poco transportable entre escenas o condiciones de captura debido a la deformación que causan la iluminación y sombras.

Cuando la misma caja se define en HSV, la semántica de los ejes cambia a favor del problema. El criterio principal de pertenencia puede concentrarse en **H**, que representa el tipo de color; luego, **S** y **V** funcionan como tolerancias sobre pureza y brillo. En términos prácticos, eso significa que el diseñador del sistema ya no necesita modelar un color como una combinación simultánea de tres intensidades absolutas, sino como un intervalo angular de tono con restricciones complementarias sobre saturación y valor. Esta reorganización es la razón técnica por la cual HSV permite umbrales más robustos en segmentación por rangos.

En OpenCV, la secuencia de trabajo recomendada es exactamente coherente con esa lógica: capturar la imagen en su formato habitual, convertirla de BGR a HSV con `cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)` y luego aplicar `cv2.inRange(hsv, lower, upper)` para construir la máscara. Desde el punto de vista del sistema, la salida binaria habilita inmediatamente etapas posteriores como conteo de píxeles, detección de contornos, centroides, bounding boxes o seguimiento por color.

La ventaja operativa sobre el TP es doble:
*   **La calibración se simplifica:** Se puede ajustar el tono objetivo con una banda relativamente estrecha de H y después ampliar o restringir S y V según el nivel de gris, brillo o sombra permitido.
*   **La estabilidad mejora:** Un mismo objeto puede sufrir cambios moderados de iluminación sin abandonar por completo la región cromática definida por H, mientras que en RGB variaría simultáneamente en tres coordenadas intensivas.

La justificación, sin embargo, debe cerrarse con una salvedad técnica indispensable para una defensa oral sólida: HSV **no** es inmune a todo cambio fotométrico. Sigue heredando la respuesta del sensor RGB y puede degradarse con saturación extrema, balance de blancos inestable, baja saturación, zonas muy oscuras o fuertes reflejos donde el tono pierde significado discriminante. En otras palabras, HSV no elimina el problema de iluminación; lo transforma en uno más manejable para umbralización por rangos. Precisamente por eso es la elección más adecuada para este TP.

---

## Conclusión

La comparación entre RGB y HSV permite establecer una conclusión técnica precisa. RGB es el espacio natural de adquisición y visualización: describe cada píxel mediante intensidades de rojo, verde y azul, es directo para pantallas y sensores y conserva la medición original del dispositivo. No obstante, para segmentación cromática basada en umbrales simples, su principal debilidad es estructural: en él, color e iluminación están mezclados. Por ello, las variaciones de brillo, sombra, reflejo o exposición desplazan el píxel dentro de un cubo tridimensional cuya interpretación cromática no resulta conveniente para la toma de decisiones por rango.

HSV, en cambio, reorganiza la misma información en términos de tono, saturación y valor. Esa reorganización no agrega información espectral nueva ni vuelve al sistema inmune a cualquier perturbación, pero sí produce una ventaja decisiva para el TP: convierte la detección por color en una operación más alineada con el significado físico-operativo de cada canal. El tono puede usarse como criterio principal de pertenencia y la saturación y el brillo como bandas de tolerancia, lo que facilita la construcción de máscaras binarias robustas mediante `cv2.inRange()` sobre imágenes previamente convertidas con `cv2.cvtColor(..., cv2.COLOR_BGR2HSV)`.

Por esa razón, HSV fue elegido adecuadamente para el Trabajo Práctico. No porque sea el mejor espacio para toda tarea de visión artificial, sino porque, para un sistema de detección de objetos por color implementado en OpenCV, ofrece mejores condiciones de ajuste, mayor estabilidad operativa frente a variaciones de iluminación y una relación más clara entre parámetro físico y decisión algorítmica.