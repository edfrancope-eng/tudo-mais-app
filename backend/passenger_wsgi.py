"""
Arquivo WSGI para Passenger (HostGator)
Este arquivo é necessário para que o Passenger (servidor web da HostGator) 
possa executar a aplicação Flask.
"""

import sys
import os

# Adicionar o diretório da aplicação ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar a aplicação Flask
from app import app as application

# Configurar para produção
if __name__ == "__main__":
    application.run()

