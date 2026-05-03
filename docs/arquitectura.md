# Arquitectura de ArquiControl

> Documento de compatibilidad. La versión oficial y actualizada de arquitectura se encuentra en `docs/06_arquitectura_del_sistema.md`.

## Resumen breve
ArquiControl está implementado como un **monolito modular** con frontend en React, backend en FastAPI y persistencia documental en MongoDB. La colección `proyectos` funciona como agregado raíz y embebe la mayor parte de la operación del sistema.

## Referencias oficiales
- Arquitectura general: `docs/06_arquitectura_del_sistema.md`
- Patrones aplicados: `docs/07_patrones_de_diseno_aplicados.md`
- Modelo no relacional: `docs/05_modelo_de_datos_no_relacional.md`
- Módulos backend y frontend: `docs/08_modulos_backend_y_frontend.md`

## Nota
Este archivo se conserva únicamente para no romper referencias previas dentro del proyecto. La documentación académica final debe tomarse de los documentos numerados de la carpeta `docs/`.