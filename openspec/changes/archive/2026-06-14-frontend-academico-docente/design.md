## Context

El shell de la aplicación (C-21) ya provee Layout con sidebar colapsable, ProtectedRoute con verificación de permisos, y AuthContext con JWT refresh automático vía axios interceptor. Las rutas actuales son solo `/login/*` y `/` (Home).

Se requiere agregar 6 nuevas capacidades del perfil PROFESOR dentro del layout protegido. Cada capacidad es una feature independiente bajo `frontend/src/features/`, siguiendo la estructura feature-based existente.

El backend ya tiene endpoints especificados en `openspec/specs/` para calificaciones (C-10), reportes/atrasados (C-11), comunicaciones (C-12), y monitores. Este change es 100% frontend — consume esos endpoints sin modificarlos.

## Goals / Non-Goals

**Goals:**
- Implementar 6 features de profesor como carpetas feature independientes bajo `frontend/src/features/`
- Extender el router con nuevas rutas protegidas, anidadas bajo el Layout existente
- Agregar entradas de navegación en el sidebar para las nuevas secciones, con visibilidad condicional por permisos
- Usar TanStack Query para fetching/caching/server state
- Usar React Hook Form + Zod para formularios (import, umbral, comunicaciones)
- Mantener consistencia visual con Tailwind CSS siguiendo los patrones del shell existente

**Non-Goals:**
- No modificar backend ni sus endpoints
- No agregar nuevas dependencias externas al frontend
- No implementar lógica de negocio del lado del cliente (es responsabilidad del backend)
- No implementar tests en este change (se cubrirán en change separado o como subtareas)

## Decisions

1. **Rutas planas bajo `/` en vez de `/app/`** — El router actual usa `/` como raíz protegida con Layout. Las nuevas rutas se agregan como hijos directos de esa ruta raíz (ej. `/calificaciones/importar`). Esto mantiene consistencia con el patrón actual y evita redirecciones innecesarias.
   - Alternativa considerada: crear `/app/*` — requeriría refactor del Layout y redirección desde `/`. Se descarta por sobreingeniería.

2. **Cada feature tiene su propio hook `useFeatureApi()`** — Encapsula todas las llamadas API de la feature usando `apiClient` directamente + TanStack Query `useQuery`/`useMutation`. Esto mantiene los componentes limpios y las queries testables.
   - Alternativa: servicios globales tipo `calificacionesService` — se descarta porque mezcla concerns y dificulta el tree-shaking.

3. **Sidebar items con `requiredPermission`** — Se extiende el array `menuItems` en `Layout.tsx` con las nuevas entradas, cada una con su permiso requerido. El filtro existente `visibleItems` ya maneja esto.
   - Alternativa: sidebar dinámico vía API — se descarta porque los permisos ya están en el JWT y los items son estáticos por release.

4. **React Router `action` + `useFetcher` NO se usan** — Aunque React Router 7 soporta data loading, el proyecto ya usa TanStack Query como capa de server state. Mezclar ambas estrategias aumenta la complejidad cognitiva sin beneficio claro.
   - Se prefiere TanStack Query para todo: queries (GET) con staleTime, mutations (POST/PUT) con invalidation, y loading/error states.

5. **Preview de importación como paso separado (wizard de 2 pasos)** — El flujo de importar calificaciones se implementa como un wizard: Paso 1 = subir archivo + preview de actividades detectadas, Paso 2 = seleccionar actividades + confirmar importación. El estado del paso 1 se mantiene en memoria (no se persiste).
   - Alternativa: modal único — se descarta porque la tabla de preview con actividades seleccionables requiere espacio vertical que un modal no provee bien.

6. **Comunicaciones: el preview es inline en la misma página** — En lugar de navegar a una página separada, el preview de la comunicación se muestra en un panel lateral o sección expandible dentro de la página de "Comunicación a atrasados", justo antes del envío.
   - Alternativa: página de preview separada — se descarta porque el usuario necesita ver el preview en contexto mientras edita el template.

## Risks / Trade-offs

- **Rendimiento en monitores con muchos alumnos** → Las tablas de monitores usan paginación server-side (parámetros `pagina` y `por_pagina` del backend). El frontend no carga todos los registros.
- **Preview de comunicación lento con muchos destinatarios** → El preview es por destinatario individual (un email a la vez). Para previsualizar múltiples, el usuario debe seleccionar uno. El envío masivo no requiere preview de cada uno.
- **Importación de archivos grandes** → El backend procesa el archivo y devuelve el preview. El frontend solo maneja la subida del archivo y la visualización de la respuesta. No hay procesamiento client-side del archivo.
- **Sidebar crece con cada feature** → Se agrupan las entradas académicas bajo un subencabezado "Académico" en el sidebar para evitar una lista plana larga. Si el número de features sigue creciendo, considerar un sidebar con submenús colapsables.
