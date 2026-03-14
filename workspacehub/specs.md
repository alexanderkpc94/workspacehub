# Project: SwiftHub - Powerful Django Project Management

## Contexto para la IA
Este es un sistema de gestión de proyectos basado en Django que incluye tableros Kanban, seguimiento de tareas y soporte de equipos. El objetivo es hacer el código totalmente accesible para un programador junior.

## Fase 1: Documentación Educativa (Junior Friendly)
- **Objetivo**: Comentar cada función, clase y lógica compleja en los módulos de `accounts`, `tasks`, `projects` y `teams` .
- **Estilo**: Los comentarios deben explicar el "por qué" de la lógica, no solo el "qué", utilizando un lenguaje claro y pedagógico .
- **Agente Responsable**: El Orquestador debe delegar esto a un subagente **Implementador**.

## Fase 2: Testing con TestSprite (MCP)
- **Objetivo**: Una vez documentado, validar la integridad del sistema.
- **Herramienta**: Utilizar exclusivamente el servidor **MCP de TestSprite** asociado a OpenCode.
- **Alcance**: Crear tests unitarios y de integración para las funcionalidades críticas (Kanban y asignación de tareas).
- **Flujo**: Aplicar el patrón **TDD** (primero crear el test que falla y luego asegurar que pase).