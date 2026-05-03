# 01. Planteamiento del problema y objetivos

## Contexto del arquitecto independiente
En la práctica profesional del arquitecto independiente, la gestión de clientes, contratos, avances, compras, pagos, documentos y proveedores suele depender de herramientas aisladas: hojas de cálculo, carpetas de archivos, mensajería informal y anotaciones manuales. Esta fragmentación genera pérdida de trazabilidad, duplicidad de registros y dificultades para obtener una visión confiable del estado de cada proyecto.

## Problema actual de organización y control
El problema que ArquiControl aborda puede resumirse en tres dimensiones:

1. **Desorganización operativa:** los datos de seguimiento, compras, contratistas y documentos no están centralizados.
2. **Déficit de control financiero:** resulta difícil conocer el saldo pendiente, el costo ejecutado y el margen estimado por proyecto en tiempo real.
3. **Baja trazabilidad:** las modificaciones o bajas de información pueden quedar sin sustento documental ni razón explícita si no existe auditoría integrada.

## Objetivo general
Desarrollar un sistema web integral que permita a un arquitecto independiente gestionar de forma centralizada sus clientes y proyectos, conservando trazabilidad operativa, control financiero y consistencia documental mediante una arquitectura modular y un modelo de datos no relacional.

## Objetivos específicos
- Centralizar la información de clientes, contratistas, proveedores y materiales.
- Modelar el proyecto como agregado raíz que embebe subregistros operativos relacionados.
- Permitir el registro y seguimiento de fases, avances, pagos, compras y documentos.
- Mantener un resumen financiero recalculado automáticamente con base en la operación real.
- Implementar una bitácora operativa visible para auditoría y revisión técnica.
- Garantizar bajas lógicas con motivo obligatorio para preservar trazabilidad.
- Ofrecer reportes básicos exportables a partir de la información consolidada.
- Sustentar la solución con patrones de diseño observables en el código real.