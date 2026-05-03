# 00. Resumen ejecutivo

## Descripción ejecutiva de ArquiControl
ArquiControl es un sistema de información web orientado a la gestión integral de proyectos para un arquitecto independiente. El sistema reúne, dentro de una misma plataforma, la administración de clientes, proyectos, fases, seguimientos, pagos, contratistas, compras, documentos, bitácora operativa y reportes básicos.

## Tipo de sistema
Se trata de un **sistema de gestión operativa y documental** con enfoque administrativo-técnico. Su implementación responde a un esquema full-stack con frontend React, backend FastAPI y persistencia documental en MongoDB.

## Usuario objetivo
El usuario objetivo evidenciado en la implementación es un **arquitecto independiente** o un estudio pequeño que necesita centralizar información dispersa de sus proyectos sin adoptar una estructura empresarial compleja ni un modelo relacional rígido.

## Valor principal del sistema
El valor principal de ArquiControl radica en cuatro capacidades que ya están implementadas en el código:

1. **Consolidación por proyecto:** cada proyecto concentra la información operativa relevante.
2. **Trazabilidad real:** las operaciones relevantes generan eventos de bitácora y actualizan indicadores.
3. **Control financiero integrado:** pagos, compras y pagos a contratistas afectan automáticamente el resumen financiero.
4. **Soporte documental y de auditoría:** el sistema conserva documentos, evidencia y bajas lógicas con motivo obligatorio.

## Resumen de funcionalidades implementadas
Según el estado real del sistema, ArquiControl incluye:

- autenticación con JWT y usuario persistido en MongoDB;
- dashboard con métricas, alertas, saldos, avance y bitácora reciente;
- CRUD operativo para clientes, contratistas, proveedores y materiales (listar, crear, actualizar);
- gestión de proyectos como agregado raíz documental;
- registro y edición de fases, seguimientos, pagos, asignaciones de contratistas, compras y documentos;
- cargas de archivos y enlaces por URL para documentación del proyecto;
- baja lógica de subregistros con motivo obligatorio;
- bitácora global y por proyecto con filtros;
- reportes básicos en PDF y CSV por proyecto;
- pruebas backend automatizadas y validaciones visuales/smoke documentadas.

## Estado documentado
La presente documentación se redacta sobre el estado final observable del código. No se identificaron módulos ficticios ni pantallas fuera de la implementación existente.