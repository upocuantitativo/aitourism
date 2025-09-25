## 🚨 GUÍA DE SOLUCIÓN INMEDIATA - Smart Tourism System

### ❌ Problema: "No module named 'requests'" u otros errores de dependencias

#### ⚡ **SOLUCIÓN RÁPIDA (Windows)**
```bash
# 1. Ejecutar script automático de solución
fix_dependencies.bat

# 2. Verificar instalación
python diagnostics.py --mode quick

# 3. Ejecutar sistema
python main.py --mode full
```

#### 🔧 **SOLUCIÓN MANUAL**
```bash
# 1. Activar entorno virtual
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/Mac

# 2. Instalar dependencias críticas
pip install requests pandas numpy dash plotly schedule psutil python-dateutil

# 3. Verificar importaciones
python -c "import requests, pandas, numpy, dash; print('✅ OK')"

# 4. Ejecutar sistema
python main.py --mode full
```

#### 🛟 **MODO EMERGENCIA**
```bash
# Si algunas dependencias fallan, usar modo básico
python emergency_start.py
# Dashboard limitado en: http://localhost:8050
```

#### 📋 **ALTERNATIVAS DISPONIBLES**

| Script | Descripción | Cuándo usar |
|--------|-------------|-------------|
| `fix_dependencies.bat` | Solución automática Windows | Error de dependencias |
| `quick_install.py` | Instalación Python manual | Problemas con pip |
| `emergency_start.py` | Sistema con funcionalidad mínima | Dependencias parciales |
| `diagnostics.py` | Diagnóstico completo | Verificar estado |

#### 🔍 **DIAGNÓSTICO COMPLETO**
```bash
# Verificar estado del sistema
python diagnostics.py --mode full

# Diagnóstico rápido
python diagnostics.py --mode quick

# Auto-reparación
python diagnostics.py --mode fix
```

#### 📚 **DOCUMENTACIÓN COMPLETA**
- **README.md** - Documentación principal del sistema
- **INSTALLATION.md** - Guía detallada de instalación
- **TROUBLESHOOTING.md** - Solución de problemas específicos

#### 🎯 **CONFIRMACIÓN DE ÉXITO**
El sistema funciona correctamente cuando veas:
```
🚀 Iniciando Smart Tourism Management System completo...
📊 Dashboard: http://localhost:8050
🤖 Servicios automatizados: Activos
```

Y puedas acceder al dashboard en: **http://localhost:8050**

---
💡 **Tip:** Para problemas persistentes, eliminar `venv/` y ejecutar `install_windows.bat` desde cero.
