██████╗ █████╗ ██████╗ ███████╗████████╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝
██████╔╝███████║██████╔╝█████╗ ██║ ██║
██╔══██╗██╔══██║██╔══██╗██╔══╝ ██║ ██║
██║ ██║██║ ██║██║ ██║███████╗ ██║ ██║
╚═╝ ╚═╝╚═╝ ╚═╝╚═╝ ╚═╝╚══════╝ ╚═╝ ╚═╝

# Architecture Overview

## System Layers

```
  ┌─────────┐        ┌────────────┐        ┌────────────────┐        ┌──────────────────┐
  │ Browser │ ─────> │ Flask      │ ─────> │ Formatting      │ ─────> │ Formatting       │
  │         │        │ Routes     │        │ Service         │        │ Functions         │
  └─────────┘        └────────────┘        └────────────────┘        └──────────────────┘
```

## 1. Browser

- User interface served by `templates/index.html`.
- Inputs raw text and displays live preview.
- Triggers formatting actions via JavaScript.

## 2. Flask Routes

- Receives user requests from the browser.
- Routes include:
  - `/` for the main page
  - `/format` for processing text transformations
- Validates input and forwards commands to the formatting service.

## 3. Formatting Service

- Acts as the business logic layer.
- Manages selected formatting operations.
- Applies transformation functions in a defined sequence.
- Returns cleaned text to the Flask response.

## 4. Formatting Functions

- Small, independent functions for each operation:
  - `remove_tabs()`
  - `remove_blank_lines()`
  - `collapse_spaces()`
  - `trim_whitespace()`

- Modular design makes it easy to add new transformers.
- Each function can be tested in isolation.

## Key Architecture Principles

- Separation of concerns: UI, routing, service logic, and text transformers are distinct layers.
- Modular extensibility: new formatting options plug into the service without changing the route flow.
- Privacy-first: no persistent storage, no account management.

## Deployment Notes

- Simple Flask app deployed as a lightweight web service.
- Static assets served from `static/`.
- Templates in `templates/`.
- Business logic in `services/formatter.py`.
