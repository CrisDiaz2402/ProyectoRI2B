import kagglehub

# Descargar la última versión del dataset
path = kagglehub.dataset_download("hsankesara/flickr-image-dataset")

print("Path to dataset files:", path)