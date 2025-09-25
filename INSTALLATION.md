# INSTALLATION AND QUICK START GUIDE
# Smart Tourism Management System

## 🚀 Quick Installation

### Windows
```bash
# Download and extract files to C:\Atourism\
cd C:\Atourism
install_windows.bat
```

### Linux/Mac
```bash
# Download and extract files  
cd /path/to/Atourism
chmod +x install_unix.sh
./install_unix.sh
```

## 📋 Manual Installation Steps

### 1. Prerequisites
- **Python 3.8+** (required)
- **pip** package manager
- **4GB+ RAM** (recommended)
- **2GB+ disk space**
- **Internet connection** (for data collection)

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)  
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. System Configuration
```bash
# Run complete setup
python setup.py --step all

# Or step by step:
python setup.py --step venv     # Virtual environment
python setup.py --step deps     # Dependencies  
python setup.py --step dirs     # Directory structure
python setup.py --step db       # Database setup
python setup.py --step config   # Configuration files
python setup.py --step sample   # Sample data
python setup.py --step test     # Run tests
```

### 4. Environment Variables (Optional)
```bash
# Copy template
cp .env.example .env

# Edit with your API keys
nano .env  # Linux/Mac
notepad .env  # Windows
```

**Key Configuration:**
```env
# AI Analysis (optional but recommended)
ANTHROPIC_API_KEY=your_claude_api_key_here
TRIPADVISOR_API_KEY=your_tripadvisor_api_key  

# Dashboard settings
DASHBOARD_PORT=8050
DASHBOARD_DEBUG=False

# System settings  
ENABLE_AUTO_COLLECTION=True
ENABLE_AI_ANALYSIS=True
ENABLE_PLS_ANALYSIS=True
```

## 🎯 Usage Modes

### Full System (Recommended)
```bash
python main.py --mode full
# Includes: Dashboard + Automated Services + AI Analysis
# Access: http://localhost:8050
```

### Dashboard Only
```bash  
python main.py --mode dashboard
# Interactive web interface only
# Access: http://localhost:8050
```

### Services Only  
```bash
python main.py --mode services
# Background data collection and analysis
# No web interface
```

### Initialization Only
```bash
python main.py --mode init
# Setup and initial data collection
# One-time execution
```

### Generate Reports
```bash
python main.py --mode report --region "Andalucía"
# Generate comprehensive regional report
```

## 🔧 System Administration

### Health Check & Diagnostics
```bash
# Quick health check
python diagnostics.py --mode quick

# Full system diagnostics  
python diagnostics.py --mode full

# Auto-fix common issues
python diagnostics.py --mode fix

# JSON output for monitoring
python diagnostics.py --mode full --json
```

### Task Scheduler (Automation)
```bash
# Start automated task scheduler
python scheduler.py --mode scheduler

# View scheduled tasks
python scheduler.py --mode info

# Install as system service
python scheduler.py --mode install-service
```

### Database Management
```bash
# Database statistics
python -c "
from utils import DatabaseManager
db = DatabaseManager('data/tourism_data.db')
print(db.get_table_stats('integrated_data'))
"

# Create backup
python -c "
from utils import DatabaseManager  
db = DatabaseManager('data/tourism_data.db')
backup_path = db.backup_database()
print(f'Backup created: {backup_path}')
"
```

### Testing
```bash
# Run all tests
python tests.py

# Run specific test category
python -m unittest tests.TestDataCollectors
python -m unittest tests.TestPLSSEMAnalyzer  
python -m unittest tests.TestAIAgents
```

## 📊 Data Flow Architecture

```
[External Sources] → [Data Collectors] → [Database] → [PLS-SEM Analysis]
       ↓                    ↓                ↓             ↓
   INE, TripAdvisor,    Automated       SQLite DB    Statistical
   Exceltur APIs       Collection                    Modeling
                           ↓                            ↓
[Dashboard] ← [AI Analysis] ← [Results Storage] ← [Validation]
     ↓              ↓              ↓              ↓
Web Interface   Claude API    JSON Files     Bootstrap
Real-time       Local Stats   Exports        Confidence
```

## 🎛️ Configuration Reference

### Key Files
- **`config.py`** - System configuration
- **`.env`** - Environment variables  
- **`main.py`** - System orchestrator
- **`dashboard/dashboard.py`** - Web interface
- **`scheduler.py`** - Task automation

### Important Directories
- **`data/`** - Database and storage
- **`logs/`** - System logs
- **`exports/`** - Generated reports
- **`cache/`** - Temporary files
- **`backups/`** - Database backups

### Default Frequencies
- **Data Collection:** Every hour
- **AI Analysis:** Every 2 hours  
- **PLS-SEM Analysis:** Daily at 3:00 AM
- **System Maintenance:** Daily at 2:00 AM
- **Reports:** Weekly on Mondays

## 🔍 Monitoring & Alerts

### System Health Metrics
```bash
# CPU, Memory, Disk usage
python -c "
from utils import SystemMonitor
monitor = SystemMonitor()
health = monitor.get_system_health()
print(health)
"
```

### Data Quality Validation
```bash
# Validate current data
python -c "
from utils import DataValidator
import pandas as pd
import sqlite3

conn = sqlite3.connect('data/tourism_data.db')
data = pd.read_sql('SELECT * FROM integrated_data LIMIT 1000', conn)
validator = DataValidator()
result = validator.validate_dataframe(data)
print(f'Quality Score: {result[\"quality_score\"]}')
conn.close()
"
```

## 🚨 Troubleshooting

### Common Issues

**1. Dashboard not loading**
```bash
# Check port availability
python diagnostics.py --mode quick

# Try different port
DASHBOARD_PORT=8051 python main.py --mode dashboard
```

**2. Database errors**
```bash
# Recreate database
python setup.py --step db

# Check database integrity
python -c "
import sqlite3
conn = sqlite3.connect('data/tourism_data.db')
print('Tables:', [row[0] for row in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall()])
conn.close()
"
```

**3. API connection issues**
```bash
# Test connectivity
python diagnostics.py --mode full

# Use local analysis only
python main.py --mode full --no-api
```

**4. Memory issues**
```bash
# Check system resources
python diagnostics.py --mode quick

# Reduce batch size in config.py
# Set MAX_WORKERS=2 in .env
```

**5. Import errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Error Logs
```bash
# View recent logs
tail -f logs/atourism_system.log

# Search for errors
grep ERROR logs/atourism_system.log

# View component-specific logs  
grep "DataCollector" logs/atourism_system.log
grep "PLSSEMAnalyzer" logs/atourism_system.log
grep "AgentOrchestrator" logs/atourism_system.log
```

## 🔒 Security Best Practices

### API Key Management
- Store API keys in `.env` file only
- Never commit `.env` to version control
- Use environment variables in production
- Rotate keys regularly

### Database Security
- Regular backups (automated daily)
- Restrict database file permissions
- Monitor access logs
- Use SSL for external databases

### Network Security
- Firewall configuration for dashboard port
- HTTPS in production (configure SSL)
- API rate limiting
- Input validation and sanitization

## 📈 Performance Optimization

### Memory Usage
```bash
# Monitor memory usage
python -c "
import psutil
print(f'Memory: {psutil.virtual_memory().percent}%')
print(f'Available: {psutil.virtual_memory().available // 1024**3}GB')
"
```

### Database Performance
```bash
# Analyze database size
python -c "
import os
db_size = os.path.getsize('data/tourism_data.db') / 1024**2
print(f'Database size: {db_size:.1f}MB')
"

# Clean old data (keep 2 years)
python -c "
from utils import DatabaseManager
db = DatabaseManager('data/tourism_data.db')
cleaned = db.clean_old_data('integrated_data', days_to_keep=730)
print(f'Cleaned {cleaned} old records')
"
```

### Cache Management
```bash
# Clear expired cache
python -c "
from utils import CacheManager  
cache = CacheManager()
cleared = cache.clear_expired(max_age_hours=24)
print(f'Cleared {cleared} cache files')
"
```

## 🌐 Deployment Options

### Local Development
```bash
# Debug mode
DASHBOARD_DEBUG=True python main.py --mode dashboard
```

### Production Server
```bash
# Production configuration
DASHBOARD_DEBUG=False DASHBOARD_HOST=0.0.0.0 python main.py --mode full

# With reverse proxy (nginx/apache)
DASHBOARD_HOST=127.0.0.1 DASHBOARD_PORT=8050 python main.py --mode dashboard
```

### Docker Deployment (Future)
```dockerfile
# Dockerfile template
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8050
CMD ["python", "main.py", "--mode", "full"]
```

### Systemd Service (Linux)
```bash
# Install as system service
python scheduler.py --mode install-service

# Service management
sudo systemctl start atourism-system
sudo systemctl enable atourism-system
sudo systemctl status atourism-system
```

## 📞 Support & Resources

### Documentation
- **README.md** - Complete system overview
- **Code comments** - Inline documentation
- **Type hints** - Function signatures
- **Docstrings** - Method documentation

### System Information
```bash
# System version and info
python -c "
import platform
import sys
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.architecture()[0]}')
"
```

### Development
```bash
# Enable debug logging
LOG_LEVEL=DEBUG python main.py --mode full

# Development mode
DEVELOPMENT_MODE=True python main.py --mode full

# Generate synthetic data
GENERATE_SYNTHETIC_DATA=True python main.py --mode init
```

---

**Smart Tourism Management System v1.0**  
*Automated Tourism Impact Analysis with PLS-SEM and AI*

For technical support and advanced configuration, refer to the complete documentation in README.md and source code comments.
