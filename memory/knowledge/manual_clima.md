# Manual de Habilidades: Clima

Mónica, cuando un usuario te pregunte por el clima, recuerda que puedes usar tu habilidad de "buscar_clima".

## ¿Cómo usarla?

No necesitas etiquetas XML de comando. Solo usa tu entorno de Sandbox (run_python_sandbox) y ejecuta lo siguiente:

```python
import sys
sys.path.append('skills')
from buscar_clima import obtener_clima
resultado = obtener_clima("Nombre de la ciudad")
print(resultado)
```

¡Esa salida te llegará al historial de observaciones y podrás responderle al usuario exactamente cómo está el clima!
