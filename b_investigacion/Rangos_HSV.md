# Rangos HSV de Calibración

*Trabajo Práctico Nº2 — Visión Artificial — Licenciatura en Automatización y Control — UTN FRC*

---

## Introducción

En segmentación cromática, un rango HSV es un intervalo de valores de **Hue** (tono), **Saturation** (saturación) y **Value** (brillo) que se utiliza para decidir si un píxel pertenece o no a una clase de color determinada. En OpenCV, la segmentación por color se implementa típicamente convirtiendo la imagen desde BGR a HSV con `cv2.cvtColor()` y luego aplicando un umbral por intervalo con `cv2.inRange()`, precisamente porque en HSV el canal H modela el tipo de color, mientras que S y V separan, en cierta medida, la pureza cromática y la intensidad luminosa. Esa separación hace que la segmentación por color resulte más manejable que en RGB/BGR, donde la cromaticidad y la luminancia están mezcladas en los tres canales.

El concepto operativo es simple: para cada píxel $(x,y)$, se verifica si sus componentes HSV se encuentran dentro de un umbral inferior y uno superior. Si el píxel cae dentro del intervalo, se conserva en una **máscara binaria**; si no, se descarta. Esa máscara es el paso intermedio entre la información de color y la detección de objetos, porque permite luego extraer regiones conectadas, blobs o contornos. OpenCV indica además que `cv2.findContours()` trabaja sobre imágenes binarias y que el objeto a encontrar debe estar en blanco sobre fondo negro, de modo que la máscara HSV cumple exactamente ese rol en una canalización clásica de detección por color.

Una formulación útil para la defensa oral es la siguiente:

$$
M(x,y) =
\begin{cases}
255, & \text{si } H_{\min} \le H(x,y) \le H_{\max} \land S_{\min} \le S(x,y) \le S_{\max} \land V_{\min} \le V(x,y) \le V_{\max} \\
0, & \text{en otro caso}
\end{cases}
$$

En términos de implementación, el rango HSV no representa "el color verdadero" de manera universal, sino una **ventana de aceptación** que debe absorber variaciones de cámara, exposición, sombras, reflejos y balance de blancos. Por eso no se habla de un único valor HSV por color, sino de intervalos calibrables. Los umbrales HSV suelen requerir ajuste para cada producto, escena e iluminación real.

---

## Funcionamiento del modelo HSV en OpenCV

OpenCV, cuando trabaja con imágenes de 8 bits y la conversión estándar `COLOR_BGR2HSV`, utiliza la siguiente representación práctica: **H en $[0, 179]$**, **S en $[0, 255]$** y **V en $[0, 255]$**. La documentación oficial advierte además que otros programas usan escalas distintas, por lo que si se comparan valores tomados de selectores de color externos con OpenCV, es obligatorio normalizar antes de copiar los umbrales.

La razón de esta diferencia está explicitada en la documentación de conversiones de color: para imágenes de 8 bits, OpenCV calcula el HSV en el dominio habitual y luego escala los canales hacia la representación de salida. En particular, para `BGR→HSV` de 8 bits aplica, en esencia, $V \leftarrow 255V$, $S \leftarrow 255S$ y $H \leftarrow H/2$. En el modelo HSV convencional, H se expresa en grados entre 0° y 360°; OpenCV lo divide por dos para que quepa cómodamente en una codificación de un byte junto con S y V, lo que conduce al rango práctico 0–179.

Como regla de conversión de calibración, conviene recordar:

$$
H_{\text{OpenCV}} \approx \frac{H_{\text{grados}}}{2}, \qquad S_{\text{OpenCV}} \approx 255 \cdot \frac{S_{\%}}{100}, \qquad V_{\text{OpenCV}} \approx 255 \cdot \frac{V_{\%}}{100}
$$

Esto tiene una implicancia directa: un color que en un selector HSV convencional aparece como $H = 120^\circ$ no debe cargarse como 120 en OpenCV, sino aproximadamente como 60. En consecuencia, los centros teóricos de los colores ideales quedan, en OpenCV de 8 bits, alrededor de **H $\approx$ 0 para rojo**, **H $\approx$ 30 para amarillo** y **H $\approx$ 60 para verde**. Esa relación es una consecuencia directa de la escala usada por OpenCV y del círculo cromático HSV estándar.

Otra implicancia importante durante la calibración es que **H no puede interpretarse de forma aislada**. OpenCV fija $H = 0$ cuando $R = G = B$, es decir, cuando el píxel es acromático, y el tono se vuelve no confiable en regiones grises, casi grises, muy oscuras u sobreexpuestas. En otras palabras, si se umbraliza sólo H y se deja S demasiado baja o V demasiado baja/alta, aparecen falsas detecciones porque el tono deja de ser una descripción estable del color real. Por eso, en una implementación robusta, los umbrales de S y V no son accesorios: son estructurales.

---

## Rangos HSV para detección de colores

Los rangos que se proponen a continuación deben entenderse como **rangos de arranque** para OpenCV en 8 bits, orientados a objetos opacos, cámaras RGB comunes y condiciones de laboratorio o campo cercano con exposición razonable. No son universales: se derivan de la codificación HSV de OpenCV, de la posición angular de cada color en el círculo HSV y de criterios prácticos para tolerar sombras, reflejos y variaciones de captura. La necesidad de ajustar experimentalmente estos límites es indispensable cuando cambian el producto, la cámara o el entorno luminoso.

### Verde

Para verde, el centro teórico en OpenCV se ubica alrededor de **H $\approx$ 60**. En implementación real conviene no usar un intervalo excesivamente estrecho, porque el verde cambia perceptiblemente entre superficies mates, brillantes, vegetación natural, pintura, plástico o impresiones, y además las sombras reducen V y frecuentemente también S. Por esa razón, este documento propone un rango base suficientemente amplio en H, pero manteniendo un piso mínimo de saturación para evitar que grises verdosos o fondos desaturados entren en la máscara.

| Parámetro | H | S | V |
| :--- | :---: | :---: | :---: |
| **Mínimo propuesto** | 35 | 60 | 40 |
| **Máximo propuesto** | 85 | 255 | 255 |
| **Centro de referencia** | 60 | — | — |

*Nota técnica: Este intervalo se plantea como rango de arranque para verde en OpenCV 8 bits; su anchura en H busca tolerar deriva cromática real, mientras que $S_{\min} = 60$ y $V_{\min} = 40$ evitan aceptar demasiado fondo grisáceo o ruido oscuro.*

La lógica del umbral es la siguiente: el ancho de H entre 35 y 85 admite variaciones entre verdes amarillentos y verdes algo cianes, pero todavía deja fuera buena parte del amarillo puro y del cian puro. El piso $S_{\min} = 60$ refleja una decisión deliberada: a saturaciones más bajas, el tono se vuelve menos confiable y los píxeles cercanos al gris pueden contaminar la máscara. El piso $V_{\min} = 40$ está elegido para no perder totalmente un objeto verde cuando entra en sombra, aunque en escenas muy oscuras podría requerirse bajarlo algo más a costa de mayor ruido.

Los problemas típicos de detección del verde son tres:
1.  **Confusión con fondos:** Confusión con fondos vegetales o con superficies oliva/amarillo-verdosas cuando el rango H es demasiado amplio.
2.  **Fragmentación en sombras:** La fragmentación del objeto en zonas sombreadas, porque V y S tienden a bajar.
3.  **Contaminación cromática:** La contaminación por cian o turquesa si $H_{\max}$ se lleva demasiado alto.

En laboratorio suele resolverse estrechando H; en campo, suele ser más efectivo ajustar primero $S_{\min}$ y $V_{\min}$, y luego aplicar operaciones morfológicas para limpiar la máscara.

### Amarillo

Para amarillo, el centro teórico en OpenCV se ubica alrededor de **H $\approx$ 30**. A diferencia del verde, aquí conviene usar un umbral de H más estrecho, porque el amarillo se encuentra entre rojo y verde en el círculo HSV, y un intervalo demasiado ancho lo hace invadir rápidamente naranja por un lado y verde-lima por el otro. Además, el amarillo es especialmente sensible a reflejos y sobreiluminación: en esas situaciones, la saturación cae y el valor sube, haciendo que el color se desplace visualmente hacia blanco cálido o crema.

| Parámetro | H | S | V |
| :--- | :---: | :---: | :---: |
| **Mínimo propuesto** | 20 | 80 | 80 |
| **Máximo propuesto** | 38 | 255 | 255 |
| **Centro de referencia** | 30 | — | — |

*Nota técnica: El amarillo requiere un umbral H relativamente estrecho para no absorber naranja ni verde claro, y suele necesitar $S_{\min}$ y $V_{\min}$ más altos que el verde para resistir reflejos, blancos cálidos y altas luces.*

El criterio de diseño del rango es más conservador que en verde. $H = 20\text{–}38$ deja el centro en 30 y reserva cierto margen por deriva de cámara y balance de blancos, pero sin abrir demasiado la máscara hacia colores adyacentes. $S_{\min} = 80$ busca descartar superficies blanquecinas o beige, y $V_{\min} = 80$ aprovecha una propiedad práctica del amarillo: cuando un objeto "amarillo" cae a valores de brillo muy bajos, con frecuencia deja de verse amarillo y tiende a marrón, ocre u oliva, aumentando la probabilidad de clasificación errónea. Este es un caso donde bajar mucho V para "ganar sensibilidad" suele degradar la especificidad del sistema.

Los problemas típicos de detección del amarillo son la confusión con naranja, con reflejos blancos o con fondos cálidos. Su sensibilidad a la iluminación es alta: las altas luces tienden a reducir S y elevar V, mientras que el cambio de temperatura de color del iluminante puede empujar perceptualmente el amarillo hacia zonas más verdosas o más anaranjadas. En la práctica, si aparecen demasiados falsos positivos claros, la primera corrección no suele ser estrechar H sino **subir $S_{\min}$**; si el objeto se pierde en la sombra, conviene revisar $V_{\min}$ con cuidado para no abrir el sistema a marrones y fondos cálidos.

### Rojo

Para rojo, el caso práctico es más delicado porque su tono ideal se encuentra en la vecindad de **0°/360°**, lo que en OpenCV de 8 bits se traduce en la vecindad de **0 y 179**. Por ese motivo, aunque conceptualmente se trate de un único color, operacionalmente no conviene describirlo como un solo intervalo continuo de H. Antes de abordar el caso especial en la sección siguiente, puede anticiparse el rango base propuesto en forma de dos ventanas.

| Parámetro | H | S | V |
| :--- | :---: | :---: | :---: |
| **Mínimo propuesto, máscara A** | 0 | 100 | 50 |
| **Máximo propuesto, máscara A** | 10 | 255 | 255 |
| **Mínimo propuesto, máscara B** | 170 | 100 | 50 |
| **Máximo propuesto, máscara B** | 179 | 255 | 255 |

*Nota técnica: El rojo necesita dos máscaras de H por la discontinuidad circular del tono. El piso $S_{\min} = 100$ ayuda a excluir grises, blancos y reflejos cálidos; $V_{\min} = 50$ conserva suficiente sensibilidad en sombras moderadas sin abrir excesivamente a ruido oscuro.*

La selección de $S_{\min} = 100$ es más exigente que para verde porque el rojo suele contaminarse con facilidad por tonos piel, marrones rojizos, magentas débiles o reflejos anaranjados cuando la saturación cae. A la vez, $V_{\min} = 50$ intenta evitar que rojos oscuros o en penumbra desaparezcan por completo. En algunas cámaras con fuerte compresión o autoexposición agresiva puede ser necesario bajar algo el valor mínimo para conservar la detección, pero eso suele venir acompañado de más falsos positivos, por lo que debe compensarse con un mejor control de S y, si hace falta, con posprocesamiento morfológico.

Los problemas típicos del rojo son la división del color en ambos extremos de H, la pérdida de segmentación en rojos muy oscuros, y la deformación cromática producida por cambios de iluminación, sombras o reflejos. En entornos de fabricación o robótica, el color aparente del objeto puede quedar deformado por sombras, reflejos e interferencias de iluminación, dificultando automatizar un único umbral fijo. Eso se vuelve especialmente visible en rojo por su cercanía al borde circular de H.

---

## Caso especial del color rojo

El canal H en HSV no es lineal, sino **circular**. Matemáticamente, es un ángulo sobre una circunferencia cromática. La propia formulación de OpenCV para BGR $\leftrightarrow$ HSV lo deja claro: el tono puede calcularse en grados dentro de 0° a 360° y, si el resultado es negativo, se corrige sumando 360°. Esa condición expresa que 0° y 360° son el mismo punto cromático. Luego, cuando OpenCV almacena el tono en una imagen de 8 bits, divide ese ángulo por dos. Por eso el rojo aparece simultáneamente cerca de $H = 0$ y cerca de $H = 179$.

Si se define una tolerancia angular $\Delta$ alrededor del rojo ideal, el conjunto del rojo en HSV convencional puede escribirse como:

$$
R = \{H : 0 \le H \le \Delta\} \cup \{H : 360 - \Delta \le H < 360\}
$$

Y en OpenCV de 8 bits como:

$$
R_{\text{OpenCV}} = \{h : 0 \le h \le \Delta/2\} \cup \{h : 180 - \Delta/2\le h \le 179\}
$$

Tomando una tolerancia práctica de unos $20^\circ$, se obtiene el patrón muy usado en OpenCV: aproximadamente **$[0, 10]$** y **$[170, 179]$**. No es una "excepción arbitraria" del rojo, sino una consecuencia directa de que H es una variable angular y no una coordenada lineal.

En la implementación práctica, esto obliga a construir dos máscaras y luego combinarlas:

```python
lower_red_1 = np.array([0, 100, 50], dtype=np.uint8)
upper_red_1 = np.array([10, 255, 255], dtype=np.uint8)

lower_red_2 = np.array([170, 100, 50], dtype=np.uint8)
upper_red_2 = np.array([179, 255, 255], dtype=np.uint8)

mask_red_1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
mask_red_2 = cv2.inRange(hsv, lower_red_2, upper_red_2)

mask_red = cv2.add(mask_red_1, mask_red_2)
```

La elección de `cv2.add()` tiene una justificación técnica concreta: OpenCV realiza una **suma saturada por elemento**, a diferencia de la suma de NumPy que trabaja módulo 256. En una máscara binaria de 0 y 255, la suma saturada implementa de forma segura la unión de ambas regiones del rojo. Como ambas ventanas de H son disjuntas, la combinación final conserva la semántica de una sola máscara roja sin introducir desbordamientos numéricos.

---

## Influencia de la iluminación

La iluminación no modifica sólo el brillo percibido del objeto; modifica la distribución completa de H, S y V que ve la cámara. Sombras, reflejos e interferencias de iluminación deforman el color aparente del objeto y vuelven difícil sostener un único umbral fijo para todas las escenas. Incluso en ensayos controlados, la segmentación en HSV puede deteriorarse de forma muy marcada si la iluminación cae por debajo de cierto umbral.

En particular, la segmentación bajo baja iluminación disminuye el área detectada debido al decrecimiento de los valores S y V. La calidad de la iluminación puede cambiar de manera sustancial el tamaño y la continuidad de la máscara segmentada.

Las sombras tienden a **disminuir V** porque oscurecen el punto, a menudo también **disminuyen S**, mientras que la diferencia en H suele ser lo bastante moderada como para modelarse con un umbral absoluto. Eso explica por qué un $V_{\min}$ demasiado alto fragmenta el objeto en zonas sombreadas, mientras que un $S_{\min}$ demasiado alto puede borrar partes válidas del color cuando la iluminación es oblicua o insuficiente.

Los reflejos especulares generan el problema contrario. En HSV, representan regiones de **baja saturación** y **alto valor**, donde el tono deja de ser informativo o puede volverse inestable. En la práctica eso produce agujeros dentro del objeto, "blanqueamiento" de una superficie amarilla o roja, y puntos brillantes que pueden romper la coherencia de la máscara si $S_{\min}$ es demasiado bajo.

La temperatura de color del iluminante y el balance de blancos de la cámara introducen un efecto adicional: distintos iluminantes generan **color casts** (desviaciones de color) distintos sobre el mismo objeto, y la cámara intenta compensarlos mediante el balance de blancos. Si esa compensación cambia entre capturas o falla en condiciones difíciles, el color medido del objeto se desplaza en H y en S, requiriendo un reajuste de umbrales.

| Condición de iluminación | Efecto dominante en H | Efecto dominante en S | Efecto dominante en V | Consecuencia típica |
| :--- | :--- | :--- | :--- | :--- |
| **Sombra** | Cambio pequeño o moderado | Suele bajar | Baja | Pérdida parcial del objeto |
| **Reflejo especular** | H deja de ser confiable | Cae mucho | Sube mucho | Agujeros o falsos blancos |
| **Contraluz** | H puede derivar por autoajuste | Baja en el objeto | El fondo sube, el objeto baja | Fragmentación y ruido |
| **Baja iluminación** | H se vuelve menos estable | Puede bajar | Baja | Subdetección y más ruido |
| **Cambio de temperatura** | Puede desplazar cromaticidad | Varía según escena | No necesariamente compensa | Necesidad de recalibrar |

---

## Estrategias de calibración

La calibración correcta consiste en construir umbrales reproducibles para **esa cámara**, **ese objeto** y **esa iluminación**. El uso de trackbars sobre `Low H`, `High H`, `Low S`, `High S`, `Low V` y `High V` permite ajustar umbrales HSV en tiempo real sobre la escena del entorno de pruebas.

Un procedimiento de calibración recomendable para este TP es el siguiente:

1.  **Fijar la cámara lo más posible:** Conviene estabilizar exposición y balance de blancos para evitar variaciones automáticas entre cuadros.
2.  **Tomar una ROI de referencia del objeto real:** Medir el color del propio objeto en la escena final para fijar umbrales superior e inferior realistas.
3.  **Comenzar con ventanas H relativamente amplias y luego cerrar:** Partir de los centros teóricos en OpenCV —rojo 0/179, amarillo 30, verde 60— y ajustar el ancho de H en función de los falsos positivos por colores vecinos.
4.  **Ajustar después $S_{\min}$ y $V_{\min}$:** $S_{\min}$ controla la entrada de grises, blancos o colores lavados; $V_{\min}$ decide cuánto objeto en sombra se conserva y cuánto ruido oscuro entra.
5.  **Validar en varias iluminaciones reales:** Probar con luz frontal uniforme, con sombra parcial y con contraluz.
6.  **Aplicar reducción de ruido sobre la máscara:** El uso de la apertura morfológica elimina ruidos blancos aislados, y el cierre morfológico rellena huecos internos del objeto.

---

## Tabla consolidada de rangos HSV (Arranque)

La tabla siguiente resume los **rangos de arranque recomendados** para OpenCV en 8 bits. Deben leerse como líneas base de calibración, no como constantes universales. El rojo aparece desdoblado en dos filas por la discontinuidad circular del tono.

| Color | $H_{\min}$ | $S_{\min}$ | $V_{\min}$ | $H_{\max}$ | $S_{\max}$ | $V_{\max}$ | Observaciones |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Verde** | 35 | 60 | 40 | 85 | 255 | 255 | Rango amplio para verdes medios; estrechar H si el fondo tiene vegetación. |
| **Amarillo** | 20 | 80 | 80 | 38 | 255 | 255 | Mantener $S_{\min}$ alto ayuda a no capturar blancos cálidos y reflejos. |
| **Rojo A** | 0 | 100 | 50 | 10 | 255 | 255 | Primera mitad del rojo. |
| **Rojo B** | 170 | 100 | 50 | 179 | 255 | 255 | Segunda mitad del rojo; combinar con `cv2.add()`. |

---

## Conclusión

El uso de HSV en OpenCV es una solución técnicamente sólida para segmentación por color porque separa el tono de la intensidad y permite construir máscaras binarias directamente ligadas a la detección de objetos. Sin embargo, los rangos HSV deben entenderse como parámetros de trabajo calibrables y no como constantes absolutas.

Para este TP, la estabilidad del sistema depende de calibrar en conjunto H, S y V bajo pruebas reales, contemplar el caso especial del rojo con dos máscaras, y validar la máscara final con reducción de ruido y detección de contornos para evitar que la segmentación se encoja o genere falsos positivos ante variaciones fotométricas normales.