

# GitLab MR MCP

[![CI](https://github.com/amirsina-mandegari/gitlab-mr-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/amirsina-mandegari/gitlab-mr-mcp/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/gitlab-mr-mcp.svg)](https://pypi.org/project/gitlab-mr-mcp/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gitlab-mr-mcp.svg)](https://pypi.org/project/gitlab-mr-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Conecta tu asistente de IA con GitLab. Haz preguntas como _"Listar solicitudes de fusión abiertas"_, _"Mostrar revisiones para la MR #123"_, _"Obtener discusiones de commits para la MR #456"_ o _"Buscar solicitudes de fusión para la rama de características"_ directamente en tu chat.

## Tabla de Contenidos

- [Configuración Rápida](#quick-setup)
- [Qué Puedes Hacer](#what-you-can-do)
- [Opciones de Configuración](#configuration-options)
- [Solución de Problemas](#troubleshooting)
- [Referencia de Herramientas](#tool-reference)
- [Hoja de Ruta](#roadmap)
- [Desarrollo](#development)
- [Notas de Seguridad](#security-notes)
- [Soporte](#support)

## Configuración Rápida

### Instalación

```bash
# Using pipx (recommended)
pipx install gitlab-mr-mcp

# Or using uv
uv tool install gitlab-mr-mcp

# Or using pip
pip install gitlab-mr-mcp
```

> **Nota:** Se recomienda usar `pipx` o `uv tool` ya que agregan automáticamente el comando `gitlab-mcp` a tu PATH. Si usas `pip install`, asegúrate de que el directorio de scripts de Python esté en PATH, o usa la ruta completa al comando.

### Obtén tu token de GitLab

1. Ve a GitLab → Configuración → Tokens de acceso
2. Crea un token con el alcance **`read_api`** (agrega el alcance `api` si deseas acceso de escritura)
3. Copia el token

### Configura tu cliente MCP

#### Configuración Multi-Proyecto (Recomendada)

Para trabajar con **múltiples proyectos de GitLab**, agrega esto a tu configuración global de MCP (`~/.cursor/mcp.json` para Cursor):

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "gitlab-mcp",
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_ACCESS_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Esta única configuración funciona en **todos tus proyectos**. Usa `search_projects` o `list_my_projects` para encontrar IDs de proyecto, luego especifica `project_id` en tus solicitudes.

#### Configuración de Proyecto Único

Para trabajar con un **proyecto único**, puedes establecer un ID de proyecto predeterminado:

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "gitlab-mcp",
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_ACCESS_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx",
        "GITLAB_PROJECT_ID": "12345"
      }
    }
  }
}
```

Reinicia tu cliente MCP y comienza a hacerle preguntas a GitLab.

## Qué Puedes Hacer

Una vez conectado, prueba estos comandos en tu chat:

### Flujo de Trabajo Multi-Proyecto

- _"¿A qué proyectos tengo acceso?"_
- _"Buscar el proyecto backend"_
- _"Mostrar MR abiertas para el proyecto 12345"_
- _"Listar solicitudes de fusión para group/my-project"_

### Comandos de Proyecto Único

- _"Listar solicitudes de fusión abiertas"_
- _"Mostrar detalles de la solicitud de fusión 456"_
- _"Obtener revisiones y discusiones para la MR #123"_
- _"Mostrar el resumen de pruebas para la MR #456"_
- _"¿Qué pruebas fallaron en la solicitud de fusión #789?"_
- _"Mostrar el pipeline para la MR #456"_
- _"Obtener los registros de trabajo fallido para la solicitud de fusión #789"_
- _"Mostrar discusiones de commits para la MR #456"_
- _"Obtener todos los comentarios en commits de la solicitud de fusión #789"_
- _"Buscar solicitudes de fusión para la rama feature/auth-improvements"_
- _"Mostrar solicitudes de fusión cerradas que apuntan a main"_
- _"Responder a la discusión abc123 en la MR #456 con '¡Gracias por los comentarios!'"_
- _"Crear un nuevo comentario de revisión en la MR #789 preguntando sobre el manejo de errores"_
- _"Resolver la discusión def456 en la MR #123"_
- _"Aprobar la solicitud de fusión #456"_
- _"Fusionar la MR #123 con squash"_
- _"Fusionar la MR #789 cuando el pipeline tenga éxito"_

## Trabajar con Comentarios de Revisión

Las herramientas de revisión mejoradas te permiten interactuar con las discusiones de solicitudes de fusión:

1. **Primero, obtén las revisiones** para ver los IDs de discusión:

   ```
   "Mostrar revisiones para la MR #123"
   ```

2. **Responde a discusiones específicas** usando el ID de discusión:

   ```
   "Responder a la discusión abc123 en la MR #456 con 'Lo corregiré en el próximo commit'"
   ```

3. **Crea nuevos hilos de discusión** para iniciar conversaciones:

   ```
   "Crear un comentario de revisión en la MR #789 preguntando '¿Podrías agregar manejo de errores aquí?'"
   ```

4. **Resuelve discusiones** cuando los problemas se hayan solucionado:
   ```
   "Resolver la discusión def456 en la MR #123"
   ```

**Nota**: La herramienta `get_merge_request_reviews` ahora muestra los IDs de discusión y IDs de nota en la salida, facilitando referenciar discusiones específicas al responder o resolver.

## Aprobar y Fusionar

Completa el ciclo de vida de la MR con herramientas de aprobación y fusión:

1. **Aprobar una solicitud de fusión**:

   ```
   "Aprobar la MR #123"
   ```

2. **Fusionar con opciones**:

   ```
   "Fusionar la MR #456 con squash"
   "Fusionar la MR #789 y eliminar la rama de origen"
   "Fusionar la MR #123 cuando el pipeline tenga éxito"
   ```

3. **Revocar aprobación** (si es necesario):
   ```
   "Desaprobar la MR #456"
   ```

**Opciones de Fusión:**

- `squash` - Fusionar commits en un solo commit
- `should_remove_source_branch` - Eliminar rama de origen después de la fusión
- `merge_when_pipeline_succeeds` - Auto-fusión cuando el pipeline tenga éxito
- `sha` - Asegurarse de que HEAD no haya cambiado (verificación de seguridad)

**Nota**: No puedes aprobar tus propias MR. La fusión fallará si la MR tiene conflictos, está en estado de borrador o no cumple con los requisitos de aprobación.

## Trabajar con Informes de Pruebas (Recomendado para Fallos de Pruebas)

GitLab proporciona dos herramientas para verificar resultados de pruebas: usa el resumen para verificaciones rápidas y el informe completo para depuración detallada:

### Opción 1: Resumen de Pruebas (Rápido y Ligero) ⚡

Usa `get_pipeline_test_summary` para un vistazo rápido:

```
"Mostrar el resumen de pruebas para la MR #123"
"¿Cuántas pruebas pasaron en la MR #456?"
```

**Lo que Obtienes:**

- 📊 Conteo de aprobadas/falladas por suite de pruebas
- ⏱️ Tiempo total de ejecución
- 🎯 Porcentaje de éxito
- ⚡ **Rápido** - no incluye mensajes de error detallados

### Opción 2: Informe Completo de Pruebas (Detallado) 🔍

Usa `get_merge_request_test_report` para depuración detallada:

```
"Mostrar el informe de pruebas para la MR #123"
"¿Qué pruebas fallaron en la solicitud de fusión #456?"
```

**Lo que Obtienes:**

- ✅ **Nombres específicos de pruebas** que pasaron/fallaron
- ❌ **Mensajes de error** y trazas de pila
- 📦 **Suites de pruebas** organizadas por clase/archivo
- ⏱️ **Tiempo de ejecución** para cada prueba
- 📊 **Tasa de éxito** y estadísticas resumen
- 📄 **Rutas de archivos** y números de línea

**Cómo Funcionan Ambas:**

- Obtiene automáticamente el pipeline más reciente para la solicitud de fusión
- Recupera datos de pruebas de ese pipeline (usa las APIs de GitLab `/pipelines/:pipeline_id/test_report` o `/test_report_summary`)

**Ejemplo de Salida:**

```
## Summary

**Total**: 45 | **Passed**: 42 | **Failed**: 3 | **Errors**: 0
**Pass Rate**: 93.3%

## Failed Tests

### [FAIL] test_login_with_invalid_password

**Duration**: 0.300s
**Class**: `tests.auth_test.TestAuth`

**Error Output**:
AssertionError: Expected 401, got 200
```

**¿Por Qué Usar Esto en Lugar de los Registros de Trabajo?**

- 🎯 **Sin ruido**: Solo resultados de pruebas, sin salida de compilación/configuración
- 📊 **Datos estructurados**: Fáciles de entender para la IA y sugerir correcciones
- 🚀 **Rápido**: Mucho más pequeño que los registros completos de trabajo
- 🔍 **Preciso**: Muestra nombres exactos de pruebas y ubicaciones de errores

**Requisitos:**

Tu CI debe subir los resultados de pruebas usando `artifacts:reports:junit` en `.gitlab-ci.yml`:

```yaml
test:
  script:
    - pytest --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
```

## Trabajar con Trabajos y Registros de Pipeline

Las herramientas de pipeline proporcionan un flujo de trabajo en dos pasos para depurar fallos de pruebas:

### Paso 1: Obtener Vista General del Pipeline

Usa `get_merge_request_pipeline` para ver todos los trabajos y sus estados:

```
"Mostrar el pipeline para la MR #456"
```

**Lo que Obtienes:**

- Vista general del pipeline (estado, duración, cobertura)
- Todos los trabajos agrupados por estado (fallido, en ejecución, exitoso)
- **IDs de trabajo** para cada trabajo (úsalos para obtener registros)
- Enlaces directos para ver trabajos en GitLab
- Información de tiempo y etapa a nivel de trabajo

### Paso 2: Obtener Registros de Trabajo Específicos

Usa `get_job_log` con un ID de trabajo para obtener la salida real:

```
"Obtener el registro para el trabajo 12345"
"Mostrar la salida del trabajo 67890"
```

**Lo que Obtienes:**

- Salida/traza completa del trabajo
- Tamaño del registro y conteo de líneas
- Truncado automáticamente a los últimos 15,000 caracteres para registros muy largos

### Flujo de Trabajo Típico:

```
Tú: "Mostrar el pipeline para la MR #123"
IA: "El pipeline falló. 2 trabajos fallaron:
     - test-unit (ID de Trabajo: 12345)
     - test-integration (ID de Trabajo: 67890)"

Tú: "Obtener el registro para el trabajo 12345"
IA: [Muestra la salida completa de pruebas con detalles del error]

Tú: "Corregir la prueba que falla"
IA: [Analiza el registro y sugiere correcciones]
```

**¿Por Qué Dos Herramientas?**

- **Rendimiento**: Solo obtiene registros cuando es necesario (no todos a la vez)
- **Flexibilidad**: Revisa el registro de cualquier trabajo (fallido, exitoso o en ejecución)
- **Eficiencia de Contexto**: Evita volcar registros enormes innecesariamente

## Trabajar con Discusiones de Commits

La herramienta `get_commit_discussions` proporciona información completa sobre discusiones y comentarios en commits individuales dentro de una solicitud de fusión:

1. **Ver todas las discusiones de commits** para una solicitud de fusión:

   ```
   "Mostrar discusiones de commits para la MR #123"
   ```

2. **Obtener historial detallado de conversaciones de commits**:

   ```
   "Obtener todos los comentarios en commits de la solicitud de fusión #456"
   ```

Esta herramienta es particularmente útil para:

- **Seguimiento de Revisión de Código**: Ver todos los comentarios en commits específicos
- **Historial de Discusiones**: Comprender la evolución de las discusiones de código
- **Contexto a Nivel de Commit**: Ver comentarios vinculados a cambios de código específicos
- **Progreso de Revisión**: Monitorear qué commits han sido discutidos

**Implementación Técnica:**

- Usa `/projects/:project_id/merge_requests/:merge_request_iid/commits` para obtener todos los commits con paginación adecuada
- Obtiene TODAS las discusiones de la solicitud de fusión usando `/projects/:project_id/merge_requests/:merge_request_iid/discussions` con soporte de paginación
- Filtra discusiones por SHA del commit usando datos de posición para mostrar conversaciones específicas del commit
- Maneja correctamente tanto comentarios individuales como hilos de discusión

La salida incluye:

- Resumen de commits totales y conteo de discusiones
- Detalles individuales de commit (SHA, título, autor, fecha)
- Todas las discusiones y comentarios para cada commit con posiciones de archivo
- Hilos de conversación completos con respuestas
- Posiciones de archivo para comentarios relacionados con diff
- Conversaciones de hilo con respuestas

## Opciones de Configuración

### Configuración MCP (Recomendada)

Configura las variables de entorno directamente en tu configuración del cliente MCP como se muestra en [Configuración Rápida](#quick-setup). Esto mantiene la configuración específica del proyecto junto al proyecto.

### Variables de Entorno

Alternativamente, establece variables de entorno en tu shell:

```bash
export GITLAB_PROJECT_ID=12345
export GITLAB_ACCESS_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
export GITLAB_URL=https://gitlab.com
```

### Soporte para Proxy SOCKS

Enruta todas las solicitudes de la API de GitLab a través de un proxy SOCKS5 estableciendo `SOCKS_PROXY`:

```json
{
  "mcpServers": {
    "gitlab-mcp": {
      "command": "gitlab-mcp",
      "env": {
        "GITLAB_URL": "https://gitlab.com",
        "GITLAB_ACCESS_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx",
        "GITLAB_PROJECT_ID": "12345",
        "SOCKS_PROXY": "socks5://127.0.0.1:1080"
      }
    }
  }
}
```

O mediante variable de entorno:

```bash
export SOCKS_PROXY=socks5://127.0.0.1:1080
```

Cuando `SOCKS_PROXY` no está establecido, las conexiones se realizan directamente (sin proxy).

### Encontrar tu ID de Proyecto

- Ve a tu proyecto de GitLab → Configuración → General → ID del Proyecto
- O verifica la URL: `https://gitlab.com/username/project` (usa el ID numérico)

## Solución de Problemas

**Error de Autenticación**: Verifica que tu token tenga permisos de `read_api` y no haya expirado.

**Proyecto No Encontrado**: Verifica dos veces que tu ID de proyecto sea correcto (es un número, no el nombre del proyecto).

**Problemas de Conexión**: Asegúrate de que tu URL de GitLab sea accesible y correcta.

**Script No Encontrado**: Asegúrate de que la ruta en tu configuración MCP apunte a la ubicación real del servidor y que el script sea ejecutable.

## Referencia de Herramientas

### Herramientas de Descubrimiento de Proyectos

| Herramienta        | Descripción                                                  | Parámetros                     |
| ------------------ | ------------------------------------------------------------ | ------------------------------ |
| `search_projects`  | **Principal** - Búsqueda rápida por nombre (usa esta primero) | `search`, `membership`, `limit`|
| `list_my_projects` | Listar todos los proyectos (más lento, usar para navegar)    | `owned`, `limit`               |

### Herramientas de Solicitudes de Fusión

Todas las herramientas con alcance de proyecto aceptan un parámetro opcional `project_id`. Si no se proporciona, utiliza la variable de entorno `GITLAB_PROJECT_ID` como respaldo.

| Herramienta                       | Descripción                                  | Parámetros                                                  |
| ------------------------------- | -------------------------------------------- | ----------------------------------------------------------- |
| `list_merge_requests`           | Listar solicitudes de fusión                 | `project_id`, `state`, `target_branch`, `limit`             |
| `get_merge_request_details`     | Obtener detalles de la MR                    | `project_id`, `merge_request_iid`                           |
| `create_merge_request`          | Crear una nueva solicitud de fusión          | `project_id`, `source_branch`, `target_branch`, `title`...  |
| `update_merge_request`          | Actualizar una solicitud de fusión existente | `project_id`, `merge_request_iid`, `title`, `assignees`...  |
| `merge_merge_request`           | Fusionar una MR                              | `project_id`, `merge_request_iid`, `squash`, `sha`...       |
| `approve_merge_request`         | Aprobar una MR                               | `project_id`, `merge_request_iid`, `sha`                    |
| `unapprove_merge_request`       | Revocar aprobación de una MR                 | `project_id`, `merge_request_iid`                           |
| `get_pipeline_test_summary`     | Obtener resumen de pruebas (vistazo rápido)  | `project_id`, `merge_request_iid`                           |
| `get_merge_request_test_report` | Obtener informes detallados de fallos de pruebas | `project_id`, `merge_request_iid`                           |
| `get_merge_request_pipeline`    | Obtener pipeline con todos los trabajos      | `project_id`, `merge_request_iid`                           |
| `get_job_log`                   | Obtener traza/salida para un trabajo específico | `project_id`, `job_id`                                      |
| `get_merge_request_reviews`     | Obtener revisiones/discusiones               | `project_id`, `merge_request_iid`                           |
| `get_commit_discussions`        | Obtener discusiones en commits               | `project_id`, `merge_request_iid`                           |
| `get_branch_merge_requests`     | Buscar MR para una rama                      | `project_id`, `branch_name`                                 |
| `reply_to_review_comment`       | Responder a una discusión existente           | `project_id`, `merge_request_iid`, `discussion_id`, `body`  |
| `create_review_comment`         | Crear nuevo hilo de discusión                 | `project_id`, `merge_request_iid`, `body`                   |
| `resolve_review_discussion`     | Resolver/no resolver discusión                | `project_id`, `merge_request_iid`, `discussion_id`          |
| `list_project_members`          | Listar miembros del proyecto                 | `project_id`                                                |
| `list_project_labels`           | Listar etiquetas del proyecto                | `project_id`                                                |

## Hoja de Ruta

### Agregado Recientemente

- **v1.4.0**: Herramientas de descubrimiento de proyectos, mejores prácticas de MCP (títulos de herramientas, anotaciones), prompts mejorados
- **v1.3.1**: Corregido conflicto de variables de entorno en múltiples espacios de trabajo en Cursor
- **v1.3.0**: Soporte para proxy SOCKS5 para enrutamiento de solicitudes de la API de GitLab
- **v1.2.0**: Herramientas para fusionar, aprobar y desaprobar MR - ciclo de vida completo de MR
- **v1.1.0**: Herramientas para crear y actualizar MR, formato de salida más limpio

### Próximamente

- [ ] **Gestión de Issues** - Listar, crear, actualizar issues y agregar comentarios
- [ ] **Comentarios en Línea** - Agregar comentarios de revisión de código en líneas específicas

### En Consideración

- [ ] Lista ligera de archivos para MR (archivos modificados sin diff completo)
- [ ] Rebase de MR vía API

### Fuera de Alcance

Las operaciones de rama, la obtención de contenido de archivos y los diff completos están intencionalmente excluidos: usa `git` localmente para estas tareas, es más rápido y capaz.

¿Tienes una solicitud de función? [Abre un issue](https://github.com/amirsina-mandegari/gitlab-mr-mcp/issues)!

## Desarrollo

### Estructura del Proyecto

```
gitlab_mr_mcp/
├── __init__.py          # Package version
├── __main__.py          # Entry point for python -m
├── server.py            # MCP server implementation
├── config.py            # Configuration management
├── gitlab_api.py        # GitLab API client
├── utils.py             # Utility functions
├── logging_config.py    # Logging configuration
└── tools/               # Tool implementations
    ├── __init__.py
    ├── list_merge_requests.py
    ├── get_merge_request_details.py
    ├── create_merge_request.py
    ├── update_merge_request.py
    └── ... (more tools)
```

### Agregar Herramientas

1. Crea un nuevo archivo en el directorio `gitlab_mr_mcp/tools/`
2. Agrega la importación y exportación a `gitlab_mr_mcp/tools/__init__.py`
3. Agrega a `list_tools()` en `gitlab_mr_mcp/server.py`
4. Agrega el manejador a `call_tool()` en `gitlab_mr_mcp/server.py`

### Agregar Prompts

Los prompts brindan orientación de flujo de trabajo a los asistentes de IA. Agrega nuevos prompts en `gitlab_mr_mcp/prompts.py`:

1. Define el contenido del prompt como una constante de cadena
2. Agrega una entrada al diccionario `PROMPTS` con `title`, `description` y `content`

```python
NEW_PROMPT = """
Your prompt content here - focus on decision trees and when to use which tool.
"""

PROMPTS = {
    # ... existing prompts ...
    "new-prompt": {
        "title": "Human Readable Title",
        "description": "Short description for prompt list",
        "content": NEW_PROMPT,
    },
}
```

### Configuración de Desarrollo

1. **Instalar dependencias de desarrollo:**

```bash
make install
# or: uv pip install -e ".[dev]"
```

2. **Comandos make disponibles:**

```bash
make install   # Install in editable mode with dev deps
make dev       # Build and install wheel locally
make test      # Run tests
make lint      # Run linters
make format    # Format code
make check     # Lint + test
make clean     # Remove build artifacts
```

3. **Configurar ganchos pre-commit:**

```bash
pre-commit install
```

Esto verificará y formateará automáticamente tu código para:

- ✨ **Espacios en blanco finales** - eliminados automáticamente
- 📄 **Problemas de fin de archivo** - corregidos automáticamente
- 🎨 **Formato de código (black)** - formateado automáticamente
- 📦 **Ordenación de imports (isort)** - organizado automáticamente
- 🐍 **Estilo Python (flake8)** - verificado con bugbear y detección de print
- 🔒 **Problemas de seguridad (bandit)** - verificaciones de seguridad
- 📋 **Formato YAML/JSON** - validado

4. **Formatear todo el código existente (solo la primera vez):**

```bash
make format
# or: black --line-length=120 . && isort --profile black --line-length=120 .
```

5. **Ejecutar pre-commit manualmente en todos los archivos:**

```bash
pre-commit run --all-files
```

### Ejecutar Pruebas

```bash
make test
# or: uv run pytest tests/ -v
```

## Notas de Seguridad

- Nunca hagas commit de tokens de acceso al control de versiones
- Usa tokens específicos del proyecto con permisos mínimos (alcance `read_api`)
- Rota los tokens regularmente
- Almacena los tokens en tu configuración de MCP (que no debería ser commiteada)

## Soporte

- Consulta la [documentación de la API de GitLab](https://docs.gitlab.com/ee/api/)
- Abre issues en [github.com/amirsina-mandegari/gitlab-mr-mcp](https://github.com/amirsina-mandegari/gitlab-mr-mcp)

## Licencia

Licencia MIT - consulta el archivo LICENSE para más detalles.
