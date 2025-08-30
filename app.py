#!/usr/bin/env python3
"""
Sistema de Gestión de Eventos
Aplicación web para gestionar eventos y actividades
"""

from src.prueba import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
