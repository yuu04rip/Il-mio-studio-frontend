import os
import sys

# aggiungi root al path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def test_import_main():
    # verifica solo che main.py si importi senza lanciare eccezioni
    import main  # noqa: F401