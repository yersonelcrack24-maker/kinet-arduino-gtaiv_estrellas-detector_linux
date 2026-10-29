from distutils.core import setup
from Cython.Build import cythonize
from setuptools import Extension

# Definimos la extensión con embed=True para que cree un ejecutable autónomo
extensions = [
    Extension(
        "detector_nativo", 
        ["estrellas_detector.py"],
        extra_compile_args=["-O3"]
    ]

setup(
    name="DetectorAutonomo",
    ext_modules=cythonize(
        extensions, 
        compiler_directives={'language_level': "3"},
        # Esto le dice a Cython que cree un archivo ejecutable principal (main)
        # Nota: requiere que el archivo .py tenga un bloque if __name__ == "__main__":
    )
)