"""
Script de instalación y configuración del Dashboard de Puertos
Autor: Consultora Port Optimization
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def install_requirements():
    """Instalar dependencias requeridas"""
    requirements = [
        'streamlit>=1.28.0',
        'pandas>=2.0.0',
        'plotly>=5.15.0',
        'requests>=2.31.0',
        'numpy>=1.24.0',
        'openpyxl>=3.1.0',  # Para exportar a Excel
        'beautifulsoup4>=4.12.0',  # Para scraping si es necesario
        'python-dotenv>=1.0.0',  # Para variables de entorno
    ]
    
    print("📦 Instalando dependencias...")
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ {req} instalado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {req}: {e}")
            return False
    return True

def create_project_structure():
    """Crear estructura de directorios del proyecto"""
    directories = [
        'data',
        'data/raw',
        'data/processed',
        'config',
        'logs',
        'exports',
        'assets'
    ]
    
    print("📁 Creando estructura de directorios...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {directory}")
    
    return True

def create_config_files():
    """Crear archivos de configuración necesarios"""
    
    # config.json
    config = {
        "api_keys": {
            "observatorio_logistico": "YOUR_API_KEY_HERE",
            "worldbank": "",
            "lloyd_list": "YOUR_LLOYD_LIST_KEY_HERE"
        },
        "endpoints": {
            "cppi_chile": "datastreams/INDIC-DE-DESEM-DE-68551/data.json",
            "contenedores_chile": "datastreams/CONTE-TERMI-ESTAT-DE-CHILE/data.json",
            "carga_puertos": "datastreams/CARGA-PUERT-CHILE/data.json"
        },
        "dashboard_config": {
            "title": "Dashboard Comparativo Puertos Chile vs Top Performers",
            "theme": "plotly_white",
            "default_ports_chile": ["Puerto Coronel", "Puerto Valparaíso", "Puerto San Antonio"],
            "default_ports_world": ["Yangshan (China)", "Singapur", "Algeciras (España)"],
            "update_frequency_hours": 24,
            "cache_duration_minutes": 60
        },
        "export_settings": {
            "formats": ["csv", "excel", "json"],
            "include_metadata": true,
            "date_format": "%Y-%m-%d %H:%M:%S"
        }
    }
    
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✅ config.json creado")
    
    # .env template
    env_template = """# API Keys para fuentes de datos
OBSERVATORIO_LOGISTICO_API_KEY=your_api_key_here
LLOYD_LIST_API_KEY=your_lloyd_list_key_here

# Configuración de la aplicación
DEBUG=True
LOG_LEVEL=INFO
DATA_UPDATE_INTERVAL=3600

# Configuración de base de datos (opcional)
# DATABASE_URL=postgresql://user:pass@localhost/portdb
"""
    
    with open('.env.template', 'w') as f:
        f.write(env_template)
    print("✅ .env.template creado")
    
    # requirements.txt
    requirements_txt = """streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.15.0
requests>=2.31.0
numpy>=1.24.0
openpyxl>=3.1.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_txt)
    print("✅ requirements.txt creado")
    
    return True

def create_launch_scripts():
    """Crear scripts para ejecutar la aplicación"""
    
    # run_dashboard.py
    run_dashboard = """#!/usr/bin/env python3
\"\"\"
Script para ejecutar el dashboard
\"\"\"

import subprocess
import sys
from pathlib import Path

def main():
    # Verificar que estamos en el directorio correcto
    if not Path('port_dashboard.py').exists():
        print("❌ No se encuentra port_dashboard.py")
        print("Asegúrate de estar en el directorio correcto del proyecto")
        return
    
    print("🚢 Iniciando Dashboard de Puertos...")
    print("📊 El dashboard se abrirá en tu navegador automáticamente")
    print("🔗 URL local: http://localhost:8501")
    print("⏹️  Para detener: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "port_dashboard.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\\n👋 Dashboard detenido")
    except Exception as e:
        print(f"❌ Error al ejecutar dashboard: {e}")

if __name__ == "__main__":
    main()
"""
    
    with open('run_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(run_dashboard)
    print("✅ run_dashboard.py creado")
    
    # run_data_collection.py
    run_collection = """#!/usr/bin/env python3
\"\"\"
Script para ejecutar la recolección de datos
\"\"\"

from data_collector import main as collect_data
import sys

def main():
    print("🔄 Iniciando recolección de datos...")
    try:
        datasets = collect_data()
        print("✅ Recolección de datos completada")
        print(f"📊 Datasets disponibles: {list(datasets.keys())}")
        return True
    except Exception as e:
        print(f"❌ Error en recolección de datos: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
    
    with open('run_data_collection.py', 'w', encoding='utf-8') as f:
        f.write(run_collection)
    print("✅ run_data_collection.py creado")
    
    # Script batch para Windows
    batch_script = """@echo off
echo 🚢 Dashboard de Puertos - Iniciando...
echo.
python run_dashboard.py
pause
"""
    
    with open('start_dashboard.bat', 'w') as f:
        f.write(batch_script)
    print("✅ start_dashboard.bat creado (Windows)")
    
    # Script bash para Linux/Mac
    bash_script = """#!/bin/bash
echo "🚢 Dashboard de Puertos - Iniciando..."
echo ""
python3 run_dashboard.py
"""
    
    with open('start_dashboard.sh', 'w') as f:
        f.write(bash_script)
    
    # Hacer ejecutable en sistemas Unix
    try:
        os.chmod('start_dashboard.sh', 0o755)
        print("✅ start_dashboard.sh creado (Linux/Mac)")
    except:
        print("⚠️ start_dashboard.sh creado (no se pudo hacer ejecutable)")
    
    return True

def create_readme():
    """Crear README con instrucciones"""
    
    readme_content = """# 🚢 Dashboard Comparativo de Puertos
## Chile vs Top Performers Mundiales

### 📋 Descripción
Dashboard interactivo para analizar y comparar el desempeño de puertos chilenos con los mejores puertos del mundo, basado en métricas del Container Port Performance Index (CPPI) y otros indicadores operacionales.

### 🎯 Objetivo
Identificar oportunidades de mejora en puertos chilenos mediante benchmarking con top performers mundiales, para proponer soluciones estratégicas de optimización y automatización.

### 📊 Funcionalidades
- **Comparación Visual**: Gráficos interactivos de métricas clave
- **Análisis de Brechas**: Radar charts multidimensionales
- **KPIs en Tiempo Real**: Métricas operacionales actualizadas
- **Recomendaciones**: Modelos de referencia basados en best practices
- **Exportación**: Datos y análisis en múltiples formatos

### 🚀 Instalación Rápida

1. **Clonar y configurar:**
   ```bash
   git clone <repository>
   cd port-dashboard
   python setup.py
   ```

2. **Configurar APIs (opcional):**
   - Editar `config.json`
   - Agregar API keys del Observatorio Logístico Chile
   - Configurar otras fuentes de datos

3. **Ejecutar dashboard:**
   ```bash
   python run_dashboard.py
   ```
   O usar los scripts de inicio:
   - Windows: `start_dashboard.bat`
   - Linux/Mac: `./start_dashboard.sh`

### 📁 Estructura del Proyecto
```
port-dashboard/
├── port_dashboard.py          # Dashboard principal
├── data_collector.py          # Recolección de datos
├── config.json               # Configuración
├── data/                     # Datos procesados
├── logs/                     # Archivos de log
├── exports/                  # Exportaciones
└── README.md                # Este archivo
```

### 📊 Fuentes de Datos
- **Container Port Performance Index (CPPI)** - Banco Mundial
- **Observatorio Logístico Chile** - Ministerio de Transportes
- **UNCTAD Maritime Statistics** - Naciones Unidas
- **Informes especializados** - Autoridades portuarias

### 🔧 Configuración Avanzada

#### APIs Soportadas:
1. **Observatorio Logístico Chile**
   ```json
   "observatorio_logistico": "YOUR_API_KEY"
   ```

2. **Lloyd's List Intelligence** (opcional)
   ```json
   "lloyd_list": "YOUR_LLOYD_LIST_KEY"
   ```

#### Personalización:
- Modificar `config.json` para ajustar puertos por defecto
- Cambiar tema visual en dashboard_config
- Configurar frecuencia de actualización

### 📈 Métricas Disponibles
- **CPPI Score**: Eficiencia general del puerto
- **TEU Anual**: Throughput de contenedores
- **Productividad de Muelle**: Movimientos por hora
- **Tiempo en Puerto**: Duración promedio de estadía
- **Nivel de Automatización**: Porcentaje de procesos automatizados
- **Conectividad Ferroviaria**: Integración con red ferroviaria
- **Sistemas Digitales**: Nivel de digitalización

### 🎯 Casos de Uso
1. **Análisis de Competitividad**: Comparar puertos chilenos con benchmarks
2. **Identificación de Brechas**: Detectar áreas de mejora prioritarias
3. **Planificación Estratégica**: Basar decisiones en datos concretos
4. **Propuestas de Valor**: Fundamentar servicios de consultoría

### 🛠️ Solución de Problemas

**Error de conexión API:**
- Verificar API keys en `config.json`
- Revisar conectividad a internet
- El dashboard funciona con datos simulados sin APIs

**Error de dependencias:**
```bash
pip install -r requirements.txt
```

**Puerto ocupado (8501):**
```bash
streamlit run port_dashboard.py --server.port=8502
```

### 📞 Soporte
Para soporte técnico o consultas sobre implementación:
- Email: consultoria@portoptimization.cl
- LinkedIn: [Port Optimization Consulting]

### 📄 Licencia
Uso interno para fines de consultoría y análisis estratégico.

---
**Desarrollado por**: Consultora Port Optimization Chile  
**Versión**: 1.0  
**Fecha**: Septiembre 2024  
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ README.md creado")
    
    return True

def main():
    """Función principal de instalación"""
    print("🚢 INSTALACIÓN DEL DASHBOARD DE PUERTOS")
    print("=" * 50)
    
    steps = [
        ("Instalando dependencias", install_requirements),
        ("Creando estructura de directorios", create_project_structure),
        ("Creando archivos de configuración", create_config_files),
        ("Creando scripts de ejecución", create_launch_scripts),
        ("Creando documentación", create_readme),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Error en: {step_name}")
            return False
        print(f"✅ {step_name} completado")
    
    print("\n" + "=" * 50)
    print("🎉 INSTALACIÓN COMPLETADA!")
    print("=" * 50)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Configurar APIs en config.json (opcional)")
    print("2. Ejecutar: python run_dashboard.py")
    print("3. Abrir http://localhost:8501 en tu navegador")
    
    print("\n📁 ARCHIVOS CREADOS:")
    files_created = [
        "config.json - Configuración principal",
        "requirements.txt - Dependencias",
        "run_dashboard.py - Ejecutar dashboard", 
        "run_data_collection.py - Recolectar datos",
        "start_dashboard.bat/.sh - Scripts de inicio",
        "README.md - Documentación completa"
    ]
    
    for file_desc in files_created:
        print(f"  ✅ {file_desc}")
    
    print(f"\n🗂️ DIRECTORIOS CREADOS:")
    dirs_created = ["data/", "logs/", "exports/", "config/", "assets/"]
    for dir_desc in dirs_created:
        print(f"  📁 {dir_desc}")
    
    print("\n🚀 Para empezar, ejecuta:")
    print("   python run_dashboard.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)