# 🚨 SOLUCIÓN RÁPIDA - Error "No module named 'requests'"

## ⚡ Solución Inmediata (Windows)

```bash
# 1. Ejecutar el script de solución automática
fix_dependencies.bat

# 2. Si falla, instalación manual:
pip install requests pandas numpy dash plotly schedule psutil python-dateutil

# 3. Probar el sistema:
python main.py --mode full
```

## 🔧 Solución Paso a Paso

### 1. **Activar Entorno Virtual**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac  
source venv/bin/activate
```

### 2. **Instalar Dependencias Críticas**
```bash
# Actualizar pip primero
python -m pip install --upgrade pip

# Instalar dependencias una por una
pip install "requests>=2.25.0"
pip install "pandas>=1.3.0" 
pip install "numpy>=1.20.0"
pip install "dash>=2.0.0"
pip install "plotly>=5.0.0"
pip install "schedule>=1.1.0"
pip install "psutil>=5.8.0"
pip install "python-dateutil>=2.8.0"
```

### 3. **Verificar Instalación**
```bash
# Probar importaciones
python -c "import requests; print('✅ requests OK')"
python -c "import pandas; print('✅ pandas OK')"
python -c "import numpy; print('✅ numpy OK')"
python -c "import dash; print('✅ dash OK')"

# Ejecutar diagnóstico
python diagnostics.py --mode quick
```

### 4. **Iniciar Sistema**
```bash
python main.py --mode full
# Dashboard: http://localhost:8050
```

## 🔧 Alternativas si Persiste el Error

### Opción 1: Instalación Mínima
```bash
pip install -r requirements-minimal.txt
```

### Opción 2: Instalación Manual Básica  
```bash
pip install requests pandas numpy dash plotly
```

### Opción 3: Modo Emergencia
```bash
# Si algunas dependencias fallan, usar modo emergencia
python emergency_start.py
```

### Opción 4: Reinstalación Completa
```bash
# Eliminar entorno virtual y recrear
rmdir /s venv          # Windows
rm -rf venv            # Linux/Mac

# Recrear desde cero
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements-minimal.txt
```

## 🐛 Diagnóstico de Problemas

### Verificar Python y Pip
```bash
python --version          # Debe ser 3.8+
pip --version             # Debe estar disponible
which python              # Verificar ruta (Linux/Mac)
where python              # Verificar ruta (Windows)
```

### Verificar Entorno Virtual
```bash
# Verificar que estás en el entorno virtual
python -c "import sys; print(sys.prefix)"
# Debe mostrar la ruta a tu carpeta venv/
```

### Verificar Conectividad
```bash
# Probar conexión a PyPI
pip install --dry-run requests
```

### Limpiar Cache de Pip
```bash
pip cache purge
pip install --no-cache-dir requests
```

## 📋 Solución para Errores Específicos

### Error: "Microsoft Visual C++ 14.0 is required"
```bash
# Instalar versiones precompiladas
pip install --only-binary=all pandas numpy scipy
```

### Error: "Failed building wheel"
```bash
# Instalar sin compilar
pip install --no-build-isolation package_name
```

### Error: Timeout durante instalación
```bash
# Aumentar timeout
pip install --timeout 300 package_name
```

### Error: Permisos (Windows)
```bash
# Ejecutar como administrador o usar --user
pip install --user package_name
```

## 🚀 Verificación Final

Después de la instalación, ejecutar:

```bash
# 1. Diagnóstico completo
python diagnostics.py --mode full

# 2. Tests básicos  
python -c "
import requests, pandas, numpy, dash, plotly
print('✅ Todas las dependencias críticas disponibles')
"

# 3. Inicio del sistema
python main.py --mode full
```

## 📞 Si Nada Funciona

1. **Usar script de instalación automática:**
   ```bash
   python quick_install.py
   ```

2. **Verificar versión de Python:**
   ```bash
   python --version  # Debe ser 3.8 o superior
   ```

3. **Crear nuevo entorno virtual:**
   ```bash
   python -m venv new_venv
   new_venv\Scripts\activate
   pip install requests pandas numpy dash plotly
   ```

4. **Usar modo emergencia:**
   ```bash
   python emergency_start.py
   ```

## ✅ Confirmación de Éxito

El sistema está funcionando correctamente cuando veas:

```
🚀 Iniciando Smart Tourism Management System completo...
📊 Dashboard: http://localhost:8050
🤖 Servicios automatizados: Activos
📈 Análisis PLS-SEM: Activo

Presiona Ctrl+C para detener el sistema
```

Y puedas acceder a: **http://localhost:8050**

---

**💡 Tip:** El script `fix_dependencies.bat` automatiza todo este proceso en Windows.
