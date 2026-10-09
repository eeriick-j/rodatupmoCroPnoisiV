# 👁️ Prácticas de Visión por Computador


## 👥 Autores y Autoría
* **Autores / Contributors:** Aridane Miranda Domínguez y Erick Justo Sosa
* **Asignatura:** Visión por Computador
* **Institución / Contexto:** Universidad de Las Palmas de Gran Canaria

---

## 📂 Estructura y Contenidos del Repositorio

### 1️⃣ Tarea 1: Análisis Geométrico por Filas (`Canny`)
* **Propósito:** Conteo y reducción matricial de píxeles blancos orientados horizontalmente.
* **Técnica:** Utilización de `cv2.reduce` para calcular la densidad de bordes, obtención del máximo (`maxfil`) y filtrado de las filas que superan el **90% de intensidad**.
* **Resultado:** Resaltado gráfico mediante líneas rojas sobre la imagen de contornos.

### 2️⃣ Tarea 2: Umbralización (`Sobel` vs. `Canny`)
* **Propósito:** Binarización de gradientes y análisis bidimensional cruzado (filas y columnas).
* **Técnica:** Aplicación de un umbral fijo (`cv2.threshold`) sobre el mapa de Sobel de 8 bits y localización de zonas críticas (≥ 90% del valor máximo).
* **Resultado:** Superposición de marcas geométricas sobre la imagen de referencia (*mandril*) y comparativa visual directa frente a Canny.

### 3️⃣ Demostrador Artístico 1: *My Little Piece of Privacy*
* **Propósito:** Reinterpretación computacional (*transmediación*) de la célebre instalación física de **Niklas Roy**.
* **Técnica:** Sustracción dinámica de fondo en tiempo real (`MOG2`) combinada con extracción de contornos (`Canny`) y análisis vertical por columnas (`cv2.reduce`).
* **Resultado:** Un sistema de **persianas digitales reactivas** que se despliegan de forma milimétrica sobre la silueta del usuario para blindar su intimidad frente a la cámara web.

### 4️⃣ Demostrador Artístico 2: *Esquinas Musicales Interactivas*
* **Propósito:** Creación de una interfaz gestual reactiva inspirada en instalaciones de arte sonoro.
* **Técnica:** Detección de movimiento por sustracción de fondo dividida en 4 regiones fijas (esquinas) optimizada para alta sensibilidad.
* **Resultado:** Un instrumento musical visual donde al acercar la mano a cualquier esquina, el botón se ilumina en verde y emite de forma instantánea una nota musical real mediante `winsound`.


