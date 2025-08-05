
CASO DE ESTUDIO 4: Plataforma de Recuperación Multimedia Multiformato con Ranking Personalizado

Crear una plataforma que integre texto, imagen, audio y video para realizar búsquedas multimodales (texto → imagen, voz → texto, etc.). Debe permitir ranking por similitud semántica, evaluación con métricas y feedback del usuario.

Datasets:

MSR-VTT Dataset (https://www.kaggle.com/datasets/vishnutheepb/msrvtt)

YouTube8M (https://research.google.com/youtube8m/)

Free images/audio from Flickr

Módulos del Proyecto:

Crawling de imágenes, videos, subtítulos y audios.

Procesamiento multimedia: extracción de frames, transcripción, histogramas.

Vectorización conjunta de medios (CLIP, BLIP).

Ranking por similitud e interacción usuario (estrellas, clics, likes).

Evaluación del sistema con métricas multimedia.

Dashboard e interfaz de consulta multimodal.

-------- Modulo 1 (Crawling de imágenes, videos, subtítulos y audios.): 
El modulo 1 es el crawling o busqueda de datos, se hizo manual y algunos utilizando librerias directamente (crwawling)
los archivos son: 
-descarga_flicker_imagenes.py
-descargar_msr_vtt.py
-crawling.py
Para ejecutarlos el comando es asi en (.venv) C:\Users\USER\Desktop\ProyectoRI2B>, por ejemplo: 
(.venv) C:\Users\USER\Desktop\ProyectoRI2B> python crawling.py 
(.venv) C:\Users\USER\Desktop\ProyectoRI2B> python descargar_msr_vtt.py 
...
Pero ya no es necesario ejecutar los comandos porque ya les paso el archivo .zip que contiene la carpeta raw y ahi esta todos los archivos necesarios, el zip lo descomprimen en la carpeta data. 
![alt text](image.png)

-------Modulo 2: (Procesamiento multimedia: extracción de frames, transcripción, histogramas.)
Para el modulo 2 los archivos utilizados son "processor.py" y "processorMain.py"
Se ha procesan solo 10 elementos porque son demasiados y mi compu no sporta :V, modifican el limite para procesar mas archivos ya que sus compus son mas potentes, esto genera y guarda en las carpetas: 
processed/frames
processed/histograms
processed/transcripts

Para ejecutar solo deben ejecutar el siguiente comando en su respectivo entorno virtual
(.venv) C:\Users\USER\Desktop\ProyectoRI2B> python processorMain.py

----------------Modulo 3 (Vectorización conjunta de medios (CLIP, BLIP).)-------------------
Para el modulo 3 los archivos utilizados son "vectorizer.py" y "vectorizeMain.py"
De estas carpetas se procesa todo:
processed/frames
processed/histograms
processed/transcripts

Pero de estas solo se procesa los 10 primeros (igual por rendimiento, modifiquen para que ejecute mas)
data/raw/crawled
data/raw/flickr

Para ejecutar solo deben ejecutar el siguiente comando en su respectivo entorno virtual
(.venv) C:\Users\USER\Desktop\ProyectoRI2B> python vectorizeMain.py

y el resultado se ve en embeddings todos en formato ".pny"
processed/frames
processed/texts
...

----------------Modulo 4 _ parte 1 (Ranking por similitud)---------------
para eso se utiliza utils.py que tiene el calculo del ranking y en search.py esta la interfaz y muestra los resultados, para probar se debe ejecutar: 
(.venv) C:\Users\USER\Desktop\ProyectoRI2B> streamlit run main.py y en el boton deslegable de la barra lateral escoger la segunda opcion (busqueda multimodal) 
Se mejoro la busqueda, se implemento traduccion y se modifico para evitar transcripciones vacias o sucias (es decir de audios y videos que notengan nada)
Ademas se mejoro para que muestre el contenido origian, antes solo mostraba las transcipciones y frames y no lo original. Se implemento metadata.json para mapear lo vectorizado.

---------------Modulo 4_ parte 2 (feedback)------------
se implemento boton de like y dislike y calificacion, esto se almacena en feedback.json. 

---------------Para utilizar metadata real--------------------
la metadata real se extrae ejecutando "metadata_extractor.py", esta extrae la metadata de los primeros 10 archivos de todas las carpetas de raw excepto youtube8m, y despues se utiliza en utils.py para mejorar el algoritmo de similitud


-----------youtube8m es ocpional ------------------

En el contexto de tu proyecto, la data de YouTube8M es opcional y depende de los objetivos y el alcance que quieras darle a tu plataforma.

¿Dónde se podría usar YouTube8M en tu proyecto?
YouTube8M es un dataset masivo de videos con features pre-extraídas y etiquetas, pensado para tareas de clasificación y recuperación de videos a gran escala. En tu plataforma, podrías usarlo en:

Procesamiento multimedia (Módulo 2):

Si quieres trabajar con videos reales a gran escala, puedes usar los TFRecords de YouTube8M como fuente de datos de video.
Puedes extraer features adicionales, comparar tus métodos de extracción con los features de YouTube8M, o simplemente usar los features ya extraídos para pruebas.
Vectorización y ranking (Módulo 3 y 4):

Puedes usar los embeddings (features) de YouTube8M directamente para pruebas de ranking y búsqueda de videos por similitud.
También podrías comparar los resultados de tu vectorización (CLIP, BLIP) con los embeddings de YouTube8M.
Evaluación y métricas:

Si incluyes videos de YouTube8M, puedes evaluar tu sistema con un dataset estándar y comparar tus resultados con benchmarks de la literatura.
¿Es necesaria la data de YouTube8M?
No es estrictamente necesaria para cumplir los objetivos mínimos del caso de estudio, ya que puedes trabajar solo con MSR-VTT, Flickr y tus propios datos.
Es útil si quieres escalar tu plataforma, comparar con estándares internacionales, o demostrar robustez en datasets grandes y variados.
Resumen
Puedes hacer todo el proyecto sin YouTube8M usando solo MSR-VTT y Flickr.
Usa YouTube8M si quieres trabajar con un dataset de videos mucho más grande, probar tu sistema a escala, o comparar con otros trabajos académicos.