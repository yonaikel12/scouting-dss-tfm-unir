# VALIDACIÓN METODOLÓGICA, AUDITORÍA DE DATOS REALES Y EVIDENCIA EMPÍRICA (`ModelHealthGate` & `ClusterValidator`)

## 1. Fórmulas de Ingeniería de Variables y Normalización (Capa Silver)

1. **Relativización por 90 minutos ($\ge 600$ minutos disputados; Lucey et al., 2014):**
   $$M_{\text{per90}} = \frac{X_{\text{bruto}}}{\text{Minutos Jugados}} \times 90,0$$
2. **Ajuste Defensivo por Posesión al 50% (Resolución de la Paradoja de Sobiech; Biermann, 2019; Pappalardo et al., 2019):**
   $$M_{\text{p90\_adj}} = M_{\text{per90}} \times \left(\frac{50,0}{\text{Posesión Media del Club (\%)}}\right)$$
3. **Transformación Paramétrica de Potencia de Yeo-Johnson (Yeo & Johnson, 2000):**
   $$\psi(y; \lambda) = \begin{cases} \frac{(y + 1)^\lambda - 1}{\lambda} & \text{si } y \ge 0, \lambda \neq 0 \\ \ln(y + 1) & \text{si } y \ge 0, \lambda = 0 \\ -\frac{(-y + 1)^{2 - \lambda} - 1}{2 - \lambda} & \text{si } y < 0, \lambda \neq 2 \\ -\ln(-y + 1) & \text{si } y < 0, \lambda = 2 \end{cases}$$

---

## 2. Resultados Empíricos de la Puerta de Salud Estadística (`ModelHealthGate`)

Sobre la cohorte auditada de **$N = 420$ futbolistas profesionales reales y únicos** (`src/ingestion/real_players_catalog.py`) y $p = 15$ variables estandarizadas post Yeo-Johnson:

* **Tamaño Muestral Certificado:** $N = 420 \ge 300$ (Criterio de estabilidad factorial de Tabachnick & Fidell, 2019).
* **Índice Global de Kaiser-Meyer-Olkin (Kaiser, 1974):**
  $$\text{KMO Global} = \frac{\sum_{j \neq k} r_{jk}^2}{\sum_{j \neq k} r_{jk}^2 + \sum_{j \neq k} p_{jk}^2} = \mathbf{0,9496} \ge 0,70 \quad (\text{Rango: Maravilloso})$$
* **Prueba de Esfericidad de Bartlett (Bartlett, 1950):**
  $$\chi^2_{\text{Bartlett}} = -\left(N - 1 - \frac{2p + 5}{6}\right) \ln|\mathbf{R}| = \mathbf{12416,37} \quad (gl = 105, \; p < 10^{-16} < 0,05)$$

---

## 3. Reducción de Dimensionalidad (ACP) y Asignación Semántica de Arquetipos

Aplicando conjuntamente la **Regla de Kaiser ($\lambda_k \ge 0,85 / 1,0$)** y el umbral de **Varianza Explicada Acumulada ($\ge 75\%$)** (**Jolliffe & Cadima, 2016**), el motor [`ScoutingMultivariateEngine`](file:///c:/Users/PC/Desktop/Clases%20UNIR/Trabajo%20Fin%20de%20Master/scouting_dss_tfm/src/analytics/multivariate_engine.py) retiene **$d = 3$ Componentes Principales ortogonales** que sintetizan el **$93,53\%$ de la varianza total**:
* **$PC_1$ ($65,24\%$ de la varianza):** Eje bipolar de Volumen de Finalización/Ataque vs. Volumen de Recuperación Defensiva.
* **$PC_2$ ($19,27\%$ de la varianza):** Eje de Progresión Asociativa (`progressive_passes_per90`) vs. Desequilibrio Individual (`successful_dribbles_per90`).
* **$PC_3$ ($9,02\%$ de la varianza):** Eje de Dominio Aéreo (`aerial_duels_won_per90`) y Disputa Física Directa.

### 3.1. Solución al Problema de Permutación de Etiquetas (*Label Switching*) y Sesgo Posicional
Dado que el algoritmo *K-Means* asigna identificadores enteros arbitrarios (`0, 1, 2, 3`) según la inicialización de los centroides, un mapeo estático provocaría que delanteros apareciesen etiquetados como defensas. Por ello, `ScoutingMultivariateEngine.fit_transform_gold()` implementa dos mecanismos de rigor:
1. **Asignación Semántica Basada en Centroides:** Inspecciona las medias de cada clúster en los bloques funcionales y asigna canónicamente:
   * **Clúster 0 (`Arquetipo I: Recuperador / Ancla Defensiva de Alto Volumen`):** Clúster con máxima media en entradas, intercepciones y bloqueos ajustados por posesión (integrado por `DF` y `MF` pivotes).
   * **Clúster 1 (`Arquetipo II: Organizador Progresivo / Creador Asociativo`):** Clúster con máxima media en pases progresivos y recuperaciones (integrado por `MF` organizadores y `DF` con salida de balón).
   * **Clúster 2 (`Arquetipo III: Creador y Extremo de Desequilibrio`):** Clúster con máxima media en regates exitosos, conducciones progresivas y $\text{xA}$ (integrado por `FW` extremos y `MF` mediapuntas).
   * **Clúster 3 (`Arquetipo IV: Finalizador y Referencia de Área`):** Clúster con máxima media en goles, $\text{xG}$ y tiros a puerta (integrado por `FW` delanteros centro y llegadores de área).
2. **Estandarización Equitativa de $Z_{\text{ACP\_Rendimiento}}$ dentro de cada Arquetipo Táctico:** En lugar de sumar globalmente $PC_1$ (lo que penalizaría a todos los defensas por tener signo negativo en el eje ataque-defensa), el índice de rendimiento se pondera por las comunalidades factoriales $h_j^2 = \sum_{k=1}^d L_{j,k}^2$ y se estandariza ($\mu = 0, \sigma = 1$) **dentro de cada Arquetipo Táctico**, evaluando a cada futbolista frente a sus pares de rol.

---

## 4. Validación Cruzada de Clustering: K-Means vs. Método de Ward ($K \in [3, 8]$)

| $K$ Clústeres | Silueta (K-Means) | Caliński-Harabasz | Davies-Bouldin ($\downarrow$) | Silueta (Ward) | ARI (K-Means vs. Ward) | Dictamen ($\text{ARI} \ge 0,70$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| $K = 3$ | $0,5505$ | $614,82$ | $0,6962$ | $0,5460$ | $0,9778$ | Aprobado ($\ge 0,70$) |
| **$K^* = 4$ (Óptimo)** | **$0,6402$** | **$854,00$** | **$0,5355$ (Mínimo)** | **$0,6362$** | **$0,9820$ (Máximo)** | **Óptimo Seleccionado** |
| $K = 5$ | $0,6678$ | $928,87$ | $0,6434$ | $0,6589$ | $0,9719$ | Aprobado ($\ge 0,70$) |
| $K = 6$ | $0,5914$ | $917,94$ | $0,6728$ | $0,5828$ | $0,9155$ | Aprobado ($\ge 0,70$) |
| $K = 7$ | $0,6077$ | $916,00$ | $0,6039$ | $0,6009$ | $0,9710$ | Aprobado ($\ge 0,70$) |
| $K = 8$ | $0,5431$ | $897,37$ | $0,6984$ | $0,5328$ | $0,9250$ | Aprobado ($\ge 0,70$) |

---

## 5. Delimitación Temporal de la Muestra y Condición *Point-in-Time* (`2023/24 - 2024/25`)

Desde el punto de vista econométrico y estadístico, toda validación transversal sobre rendimiento y coste requiere que el vector de características deportivas $\mathbf{x}_i$, el parámetro contextual de posesión del club $\text{Pos}_i$ y el par financiero $(\text{VM}_i, \text{Sal}_i)$ estén referidos al **mismo corte temporal de observación (`season_snapshot = "2023/24 - 2024/25"`)**:

$$\forall i \in \{1, \dots, 420\}, \quad \left(\mathbf{x}_i^{(t)}, \; \text{Club}_i^{(t)}, \; \text{Pos}_i^{(t)}, \; \text{VM}_i^{(t)}, \; \text{Sal}_i^{(t)}\right) \Big|_{t = \text{Snapshot } 2023/24\text{–}2024/25}$$

* **Justificación Matemática contra la Fuga de Datos Temporal (*Temporal Data Leakage*):** Si a un jugador cuyos minutos competitivos ($\ge 600\text{ min}$) se registraron en el club $A$ durante la temporada $t$ (por ejemplo, *Leny Yoro* en el *LOSC Lille* de la Ligue 1 francesa) se le asignase retroactivamente el club $B$ al que fue traspasado con posterioridad (*Manchester United*), el factor corrector de posesión $\left(50,0 / \text{Pos}_B\right)$ alteraría artificialmente sus métricas defensivas ajustadas $M_{\text{p90\_adj}}$ y su salario post-traspaso sesgaría el diferencial $\text{Net Value}_i = Z_{\text{ACP}, i} - Z_{\text{Coste}, i}$, destruyendo la capacidad del modelo para identificar qué jugadores eran *Gangas Tácticas* en el momento de su evaluación.
