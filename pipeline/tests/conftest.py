import os
import sys

# Os testes importam os módulos de pipeline/ diretamente e rodam a partir da raiz do repositório.
RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAIZ, "pipeline"))
os.chdir(RAIZ)
