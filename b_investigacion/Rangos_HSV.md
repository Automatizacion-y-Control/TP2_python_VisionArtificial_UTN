# Rangos_HSV.md

*Trabajo Práctico Nº2 — Visión Artificial — Licenciatura en Automatización y Control — UTN FRC*

## Introducción

En segmentación cromática, un rango HSV es un intervalo de valores de **Hue** (tono), **Saturation** (saturación) y **Value** (brillo) que se utiliza para decidir si un píxel pertenece o no a una clase de color determinada. En OpenCV, la segmentación por color se implementa típicamente convirtiendo la imagen desde BGR a HSV con `cv.cvtColor()` y luego aplicando un umbral por intervalo con `cv.inRange()`, precisamente porque en HSV el canal H modela el tipo de color, mientras que S y V separan, en cierta medida, la pureza cromática y la intensidad luminosa. Esa separación hace que la segmentación por color resulte más manejable que en RGB/BGR, donde la cromaticidad y la luminancia están mezcladas en los tres canales. citeturn3view0turn4view0turn24view3

El concepto operativo es simple: para cada píxel \((x,y)\), se verifica si sus componentes HSV se encuentran dentro de un umbral inferior y uno superior. Si el píxel cae dentro del intervalo, se conserva en una **máscara binaria**; si no, se descarta. Esa máscara es el paso intermedio entre la información de color y la detección de objetos, porque permite luego extraer regiones conectadas, blobs o contornos. OpenCV indica además que `findContours()` trabaja sobre imágenes binarias y que el objeto a encontrar debe estar en blanco sobre fondo negro, de modo que la máscara HSV cumple exactamente ese rol en una canalización clásica de detección por color. citeturn24view0turn26view0

Una formulación útil para defensa oral es la siguiente:

\[
M(x,y)=
\begin{cases}
255,& \text{si } H_{min}\le H(x,y)\le H_{max}\ \land\ S_{min}\le S(x,y)\le S_{max}\ \land\ V_{min}\le V(x,y)\le V_{max}\\
0,& \text{en otro caso}
\end{cases}
\]

En términos de implementación, el rango HSV no representa “el color verdadero” de manera universal, sino una **ventana de aceptación** que debe absorber variaciones de cámara, exposición, sombras, reflejos y balance de blancos. Por eso no se habla de un único valor HSV por color, sino de intervalos calibrables. La literatura aplicada a visión industrial y robótica remarca precisamente que los umbrales HSV suelen requerir ajuste para cada producto, escena e iluminación real. citeturn25view0turn25view2turn25view3

## Funcionamiento del modelo HSV en OpenCV

OpenCV, cuando trabaja con imágenes de 8 bits y la conversión estándar `COLOR_BGR2HSV`, utiliza la siguiente representación práctica: **H en [0,179]**, **S en [0,255]** y **V en [0,255]**. La documentación oficial advierte además que otros programas usan escalas distintas, por lo que si se comparan valores tomados de selectores de color externos con OpenCV, es obligatorio normalizar antes de copiar los umbrales. citeturn4view0

La razón de esta diferencia está explicitada en la documentación de conversiones de color: para imágenes de 8 bits, OpenCV calcula el HSV en el dominio habitual y luego escala los canales hacia la representación de salida. En particular, para `BGR→HSV` de 8 bits aplica, en esencia, \(V \leftarrow 255V\), \(S \leftarrow 255S\) y \(H \leftarrow H/2\). En el modelo HSV convencional, H se expresa en grados entre 0° y 360°; OpenCV lo divide por dos para que quepa cómodamente en una codificación de un byte junto con S y V, lo que conduce al rango práctico 0–179. citeturn4view1

Como regla de conversión de calibración, conviene recordar:

\[
H_{OpenCV}\approx \frac{H_{grados}}{2},
\qquad
S_{OpenCV}\approx 255\cdot \frac{S_{\%}}{100},
\qquad
V_{OpenCV}\approx 255\cdot \frac{V_{\%}}{100}
\]

Esto tiene una implicancia directa: un color que en un selector HSV convencional aparece como \(H=120^\circ\) no debe cargarse como 120 en OpenCV, sino aproximadamente como 60. En consecuencia, los centros teóricos de los colores ideales quedan, en OpenCV de 8 bits, alrededor de **H≈0 para rojo**, **H≈30 para amarillo** y **H≈60 para verde**. Esa relación es una consecuencia directa de la escala usada por OpenCV y del círculo cromático HSV estándar. citeturn4view1

Otra implicancia importante durante la calibración es que **H no puede interpretarse de forma aislada**. OpenCV fija \(H=0\) cuando \(R=G=B\), es decir, cuando el píxel es acromático, y la literatura técnica señala además que el tono se vuelve no confiable en regiones grises, casi grises, muy oscuras u sobreexpuestas. En otras palabras, si se umbraliza sólo H y se deja S demasiado baja o V demasiado baja/alta, aparecen falsas detecciones porque el tono deja de ser una descripción estable del color real. Por eso, en una implementación robusta, los umbrales de S y V no son accesorios: son estructurales. citeturn4view1turn14view0turn14view1

## Rangos HSV para detección de colores

Los rangos que se proponen a continuación deben entenderse como **rangos de arranque** para OpenCV en 8 bits, orientados a objetos opacos, cámaras RGB comunes y condiciones de laboratorio o campo cercano con exposición razonable. No son universales: se derivan de la codificación HSV de OpenCV, de la posición angular de cada color en el círculo HSV y de criterios prácticos para tolerar sombras, reflejos y variaciones de captura. La necesidad de ajustar experimentalmente estos límites está ampliamente documentada cuando cambian el producto, la cámara o el entorno luminoso. citeturn4view1turn25view0turn25view3turn15view0

### Verde

Para verde, el centro teórico en OpenCV se ubica alrededor de **H≈60**. En implementación real conviene no usar un intervalo excesivamente estrecho, porque el verde cambia perceptiblemente entre superficies mates, brillantes, vegetación natural, pintura, plástico o impresiones, y además las sombras reducen V y frecuentemente también S. Por esa razón, este documento propone un rango base suficientemente amplio en H, pero manteniendo un piso mínimo de saturación para evitar que grises verdosos o fondos desaturados entren en la máscara. citeturn4view1turn20view0turn14view0

| Parámetro | H | S | V |
|---|---:|---:|---:|
| Mínimo propuesto | 35 | 60 | 40 |
| Máximo propuesto | 85 | 255 | 255 |
| Centro de referencia | 60 | — | — |

*Nota técnica: este intervalo se plantea como rango de arranque para verde en OpenCV 8 bits; su anchura en H busca tolerar deriva cromática real, mientras que `Smin=60` y `Vmin=40` evitan aceptar demasiado fondo grisáceo o ruido oscuro.* citeturn4view1turn14view0turn20view0

La lógica del umbral es la siguiente: el ancho de H entre 35 y 85 admite variaciones entre verdes amarillentos y verdes algo cianes, pero todavía deja fuera buena parte del amarillo puro y del cian puro. El piso `Smin=60` refleja una decisión deliberada: a saturaciones más bajas, el tono se vuelve menos confiable y los píxeles cercanos al gris pueden contaminar la máscara. El piso `Vmin=40` está elegido para no perder totalmente un objeto verde cuando entra en sombra, aunque en escenas muy oscuras podría requerirse bajarlo algo más a costa de mayor ruido. citeturn14view0turn14view1turn20view0

Los problemas típicos de detección del verde son tres. El primero es la confusión con fondos vegetales o con superficies oliva/amarillo-verdosas cuando el rango H es demasiado amplio. El segundo es la fragmentación del objeto en zonas sombreadas, porque V y S tienden a bajar. El tercero es la contaminación por cian o turquesa si `Hmax` se lleva demasiado alto. En laboratorio suele resolverse estrechando H; en campo, suele ser más efectivo ajustar primero `Smin` y `Vmin`, y luego aplicar operaciones morfológicas para limpiar la máscara. citeturn20view0turn6view0

### Amarillo

Para amarillo, el centro teórico en OpenCV se ubica alrededor de **H≈30**. A diferencia del verde, aquí conviene usar un umbral de H más estrecho, porque el amarillo se encuentra entre rojo y verde en el círculo HSV, y un intervalo demasiado ancho lo hace invadir rápidamente naranja por un lado y verde-lima por el otro. Además, el amarillo es especialmente sensible a reflejos y sobreiluminación: en esas situaciones, la saturación cae y el valor sube, haciendo que el color se desplace visualmente hacia blanco cálido o crema. citeturn4view1turn18view2turn14view0

| Parámetro | H | S | V |
|---|---:|---:|---:|
| Mínimo propuesto | 20 | 80 | 80 |
| Máximo propuesto | 38 | 255 | 255 |
| Centro de referencia | 30 | — | — |

*Nota técnica: el amarillo requiere un umbral H relativamente estrecho para no absorber naranja ni verde claro, y suele necesitar `Smin` y `Vmin` más altos que el verde para resistir reflejos, blancos cálidos y altas luces.* citeturn4view1turn18view2turn14view0

El criterio de diseño del rango es más conservador que en verde. `H=20–38` deja el centro en 30 y reserva cierto margen por deriva de cámara y balance de blancos, pero sin abrir demasiado la máscara hacia colores adyacentes. `Smin=80` busca descartar superficies blanquecinas o beige, y `Vmin=80` aprovecha una propiedad práctica del amarillo: cuando un objeto “amarillo” cae a valores de brillo muy bajos, con frecuencia deja de verse amarillo y tiende a marrón, ocre u oliva, aumentando la probabilidad de clasificación errónea. Este es un caso donde bajar mucho V para “ganar sensibilidad” suele degradar la especificidad del sistema. citeturn14view0turn18view2turn28view0

Los problemas típicos de detección del amarillo son la confusión con naranja, con reflejos blancos o con fondos cálidos. Su sensibilidad a la iluminación es alta: las altas luces tienden a reducir S y elevar V, mientras que el cambio de temperatura de color del iluminante puede empujar perceptualmente el amarillo hacia zonas más verdosas o más anaranjadas. En práctica, si aparecen demasiados falsos positivos claros, la primera corrección no suele ser estrechar H sino **subir `Smin`**; si el objeto se pierde en sombra, conviene revisar `Vmin` con cuidado para no abrir el sistema a marrones y fondos cálidos. citeturn18view2turn28view0

### Rojo

Para rojo, el caso práctico es más delicado porque su tono ideal se encuentra en la vecindad de **0°/360°**, lo que en OpenCV de 8 bits se traduce en la vecindad de **0 y 179**. Por ese motivo, aunque conceptualmente se trate de un único color, operacionalmente no conviene describirlo como un solo intervalo continuo de H. Antes de abordar el caso especial en la sección siguiente, puede anticiparse el rango base propuesto en forma de dos ventanas. citeturn4view0turn4view1

| Parámetro | H | S | V |
|---|---:|---:|---:|
| Mínimo propuesto, máscara A | 0 | 100 | 50 |
| Máximo propuesto, máscara A | 10 | 255 | 255 |
| Mínimo propuesto, máscara B | 170 | 100 | 50 |
| Máximo propuesto, máscara B | 179 | 255 | 255 |

*Nota técnica: el rojo necesita dos máscaras de H por la discontinuidad circular del tono. El piso `Smin=100` ayuda a excluir grises, blancos y reflejos cálidos; `Vmin=50` conserva suficiente sensibilidad en sombras moderadas sin abrir excesivamente a ruido oscuro.* citeturn4view1turn14view0turn18view2

La selección de `Smin=100` es más exigente que para verde porque el rojo suele contaminarse con facilidad por tonos piel, marrones rojizos, magentas débiles o reflejos anaranjados cuando la saturación cae. A la vez, `Vmin=50` intenta evitar que rojos oscuros o en penumbra desaparezcan por completo. En algunas cámaras con fuerte compresión o autoexposición agresiva puede ser necesario bajar algo el valor mínimo para conservar la detección, pero eso suele venir acompañado de más falsos positivos, por lo que debe compensarse con un mejor control de S y, si hace falta, con posprocesamiento morfológico. citeturn14view0turn20view0turn6view0

Los problemas típicos del rojo son la división del color en ambos extremos de H, la pérdida de segmentación en rojos muy oscuros, y la deformación cromática producida por cambios de iluminación, sombras o reflejos. En entornos de fabricación o robótica, la literatura reporta explícitamente que el color aparente del objeto puede quedar deformado por sombras, reflejos e interferencias de iluminación, dificultando automatizar un único umbral fijo. Eso se vuelve especialmente visible en rojo por su cercanía al borde circular de H. citeturn25view0turn25view1

## Caso especial del color rojo

El canal H en HSV no es lineal, sino **circular**. Matemáticamente, es un ángulo sobre una circunferencia cromática. La propia formulación de OpenCV para RGB↔HSV lo deja claro: el tono puede calcularse en grados dentro de 0° a 360° y, si el resultado es negativo, se corrige sumando 360°. Esa condición expresa que 0° y 360° son el mismo punto cromático. Luego, cuando OpenCV almacena el tono en una imagen de 8 bits, divide ese ángulo por dos. Por eso el rojo aparece simultáneamente cerca de `H=0` y cerca de `H=179`. citeturn4view1

Si se define una tolerancia angular \(\Delta\) alrededor del rojo ideal, el conjunto del rojo en HSV convencional puede escribirse como:

\[
R=\{H:0\le H\le \Delta\}\ \cup\ \{H:360-\Delta\le H<360\}
\]

y en OpenCV de 8 bits como:

\[
R_{OpenCV}=\{h:0\le h\le \Delta/2\}\ \cup\ \{h:180-\Delta/2\le h\le 179\}
\]

Tomando una tolerancia práctica de unos \(20^\circ\), se obtiene el patrón muy usado en OpenCV: aproximadamente **[0,10]** y **[170,179]**. No es una “excepción arbitraria” del rojo, sino una consecuencia directa de que H es una variable angular y no una coordenada lineal. citeturn4view1

En implementación real, esto obliga a construir dos máscaras y luego combinarlas:

```python
lower_red_1 = np.array([0, 100, 50], dtype=np.uint8)
upper_red_1 = np.array([10, 255, 255], dtype=np.uint8)

lower_red_2 = np.array([170, 100, 50], dtype=np.uint8)
upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)

mask_red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
mask_red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

mask_red = cv2.add(mask_red_1, mask_red_2)
```

La elección de `cv2.add()` tiene una justificación técnica concreta: OpenCV realiza una **suma saturada por elemento**, a diferencia de la suma de NumPy que trabaja módulo 256. En una máscara binaria de 0 y 255, la suma saturada implementa de forma segura la unión práctica de ambas regiones del rojo. Como ambas ventanas de H son disjuntas, la combinación final conserva la semántica de una sola máscara roja sin introducir desbordamientos numéricos. citeturn4view2

## Influencia de la iluminación

La iluminación no modifica sólo el brillo percibido del objeto; modifica la distribución completa de H, S y V que ve la cámara. Distintos trabajos aplicados muestran que sombras, reflejos e interferencias de iluminación deforman el color aparente del objeto y vuelven difícil sostener un único umbral fijo para todas las escenas. Incluso en ensayos controlados, la segmentación en HSV puede deteriorarse de forma muy marcada si la iluminación cae por debajo de cierto umbral. citeturn25view0turn25view1turn15view0

En particular, Ambrus y colaboradores observaron que, para segmentación de tomates maduros en HSV, los resultados permanecían estables cerca de y por encima de 3000 lx, mientras que por debajo de ese nivel el área detectada comenzaba a disminuir rápidamente; alrededor de 1600 lx, la región segmentada podía caer aproximadamente a la mitad del tamaño real. Ese resultado no debe trasladarse numéricamente sin más a cualquier aplicación, pero sí es una evidencia fuerte de una idea general: **la calidad de la iluminación puede cambiar de manera sustancial el tamaño y la continuidad de la máscara segmentada**. citeturn15view0

La literatura sobre supresión de sombras en HSV aporta una lectura muy útil para calibración. Los trabajos clásicos muestran que las sombras tienden a **disminuir V** porque oscurecen el punto, a menudo también **disminuyen S**, y que la diferencia en H suele ser lo bastante moderada como para modelarse con un umbral absoluto. Eso explica por qué un `Vmin` demasiado alto fragmenta el objeto en zonas sombreadas, mientras que un `Smin` demasiado alto puede borrar partes válidas del color cuando la iluminación es oblicua o insuficiente. citeturn20view0turn19view2turn19view4

Los reflejos especulares generan el problema contrario. En HSV, la literatura los describe como regiones de **baja saturación** y **alto valor**, donde el tono deja de ser informativo o puede volverse inestable. En la práctica eso produce agujeros dentro del objeto, “blanqueamiento” de una superficie amarilla o roja, y puntos brillantes que pueden romper la coherencia de la máscara si `Smin` es demasiado bajo. citeturn18view0turn18view2turn18view3

La temperatura de color del iluminante y el balance de blancos de la cámara introducen un efecto adicional: distintos iluminantes generan **color casts** distintos sobre el mismo objeto, y la cámara intenta compensarlos mediante white balance. Si esa compensación cambia entre capturas o falla en condiciones difíciles, el color medido del objeto se desplaza; en términos de HSV, eso implica por inferencia práctica que el umbral de H y, en menor medida, el de S también pueden necesitar reajuste. Fuentes de ingeniería de imagen remarcan que distintas temperaturas de color producen color casts diferentes sobre el mismo objeto y que, sin un white balance adecuado, el color del objeto no aparece con su color real. citeturn28view0turn27search17

| Condición de iluminación | Efecto dominante en H | Efecto dominante en S | Efecto dominante en V | Consecuencia típica |
|---|---|---|---|---|
| Sombra | cambio pequeño o moderado | suele bajar | baja | pérdida parcial del objeto |
| Reflejo especular | H deja de ser confiable | cae mucho | sube mucho | agujeros o falsos blancos |
| Contraluz | H puede derivar por autoajuste de cámara | baja en el objeto | el fondo sube y el objeto baja | fragmentación y ruido |
| Baja iluminación | H se vuelve menos estable | puede bajar | baja | subdetección y más ruido |
| Cambio de temperatura de color | puede desplazar cromaticidad | varía según la escena | no necesariamente compensa | necesidad de recalibrar |

*La tabla resume efectos descritos por trabajos sobre sombras, reflejos, iluminación y white balance en visión por computador y en captura digital.* citeturn20view0turn18view2turn15view0turn28view0

## Estrategias de calibración

La calibración correcta no consiste en “copiar rangos de Internet”, sino en construir umbrales reproducibles para **esa cámara**, **ese objeto** y **esa iluminación**. La documentación de OpenCV propone explícitamente el uso de trackbars sobre `Low H`, `High H`, `Low S`, `High S`, `Low V` y `High V` para ajustar umbrales HSV en tiempo real, y la literatura aplicada al entorno industrial señala que el umbral suele depender del objeto, del producto y de las condiciones luminosas del entorno. citeturn3view0turn5view0turn25view0turn25view3

Un procedimiento de calibración recomendable para este TP es el siguiente:

1. **Fijar la cámara lo más posible.** Si el hardware lo permite, conviene estabilizar exposición y balance de blancos, o al menos registrar cómo están configurados, porque variaciones automáticas entre cuadros introducen desplazamientos cromáticos y de brillo. Además, incluso bajo condiciones equivalentes, distintas cámaras no necesariamente entregan los mismos valores de color. citeturn28view0turn15view0  
2. **Tomar una ROI de referencia del objeto real.** La estrategia más sólida es medir el color del propio objeto en la escena final. Los trabajos de localización HSV por ROI usan precisamente una región de referencia para extraer H, S y V y fijar umbrales superiores e inferiores a partir de esos valores. citeturn25view3  
3. **Comenzar con ventanas H relativamente amplias y luego cerrar.** Conviene partir de centros teóricos en OpenCV —rojo 0/179, amarillo 30, verde 60— y ajustar primero el ancho de H en función de los falsos positivos por colores vecinos. citeturn4view1  
4. **Ajustar después `Smin` y `Vmin`.** En general, `Smin` controla la entrada de grises, blancos o colores lavados; `Vmin` decide cuánto objeto en sombra se conserva y cuánto ruido oscuro entra. Como el tono se vuelve problemático en regiones grises, oscuras o sobreexpuestas, este paso suele ser más decisivo que afinar un único grado de H. citeturn14view0turn14view1  
5. **Validar en varias iluminaciones reales.** No alcanza con una sola mesa bien iluminada. Debe probarse, como mínimo, con luz frontal uniforme, con sombra parcial y con una situación de contraluz o exceso de brillo, porque la literatura muestra que la segmentación puede variar mucho con la iluminación disponible. citeturn15view0turn25view1  
6. **Aplicar reducción de ruido sobre la máscara.** En OpenCV, la apertura elimina pequeños ruidos blancos y el cierre rellena pequeños agujeros negros dentro del objeto. En sistemas reales esto mejora notablemente la estabilidad del contorno antes de medir área, centroide o bounding box. citeturn6view0turn26view0  

En entornos más controlados, es útil complementar el ajuste visual con datos. Ambrus et al. determinaron intervalos HSV a partir de histogramas de color obtenidos bajo distintas iluminaciones, mientras que propuestas más recientes en robótica usan una ROI de referencia para extraer automáticamente los límites superior e inferior. Para un TP universitario, una versión práctica de esa idea es calcular valores medios o percentiles en una ROI del color objetivo, usar esos datos como intervalo inicial y luego terminar el ajuste fino con trackbars. Esa combinación reduce subjetividad y deja una justificación experimental más defendible. citeturn15view0turn25view3

## Tabla consolidada de rangos HSV

La tabla siguiente resume los **rangos de arranque recomendados** por este documento para OpenCV en 8 bits. Deben leerse como líneas base de calibración, no como constantes universales. El rojo aparece desdoblado en dos filas por la discontinuidad circular del tono. citeturn4view0turn4view1turn25view0turn15view0

| Color | Hmin | Smin | Vmin | Hmax | Smax | Vmax | Observaciones |
|---|---:|---:|---:|---:|---:|---:|---|
| Verde | 35 | 60 | 40 | 85 | 255 | 255 | Rango amplio para verdes medios; si el fondo tiene vegetación, conviene estrechar H. |
| Amarillo | 20 | 80 | 80 | 38 | 255 | 255 | Mantener `Smin` alto ayuda a no capturar blancos cálidos y reflejos. |
| Rojo A | 0 | 100 | 50 | 10 | 255 | 255 | Primera mitad del rojo. |
| Rojo B | 170 | 100 | 50 | 179 | 255 | 255 | Segunda mitad del rojo; combinar con `cv2.add()`. |

Estas observaciones técnicas son importantes para la defensa oral. Primero, los valores superiores de S y V se dejan en 255 porque, en un sistema de segmentación por color, el control de robustez suele recaer más sobre los límites inferiores y sobre el ancho de H que sobre “cortar” el extremo alto. Segundo, si se detectan demasiadas superficies claras no deseadas, la intervención más efectiva suele ser subir `Smin`; si el objeto se pierde en sombra, la corrección más razonable suele ser revisar `Vmin`; y si se absorben colores vecinos, entonces corresponde estrechar H. Tercero, si la escena cambia mucho de una condición a otra, suele ser mejor almacenar perfiles diferentes por iluminación que forzar un único rango universal. citeturn14view0turn18view2turn20view0turn25view1

## Conclusión

El uso de HSV en OpenCV es una solución técnicamente sólida para segmentación por color porque separa el tono de la intensidad y permite construir máscaras binarias directamente ligadas a la detección de objetos. Sin embargo, esa ventaja no elimina el problema central de toda segmentación cromática: el color medido por la cámara depende del iluminante, de los reflejos, de la sombra, del balance de blancos, de la exposición y del propio sensor. Por eso los rangos HSV deben entenderse como parámetros de trabajo calibrables y no como constantes absolutas. citeturn3view0turn4view1turn25view0turn15view0

Para este TP, la conclusión operativa es clara: la estabilidad del sistema no depende sólo de elegir bien `Hmin` y `Hmax`, sino de calibrar en conjunto H, S y V bajo pruebas reales, de contemplar el caso especial del rojo con dos máscaras, y de validar la máscara final con reducción de ruido y detección de contornos. La literatura revisada muestra que, sin esa calibración experimental, la segmentación puede encogerse, fragmentarse o generar falsos positivos ante cambios relativamente normales de iluminación. En consecuencia, la defensa técnica correcta no es afirmar que un color “vale tal número”, sino justificar por qué un intervalo fue elegido, cómo fue ajustado y bajo qué condiciones de captura se considera confiable. citeturn4view2turn6view0turn20view0turn15view0