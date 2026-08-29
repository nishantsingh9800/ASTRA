# ASTRA 2.0 Accessibility Architecture

ASTRA is built on the principle that the assistant adapts to the user, not the other way around. Every core feature must be accessible across multiple modalities.

## Supported Input Modalities
- **Voice / Speech**
- **Keyboard / Mouse / Touch**
- **Sign Language Recognition:** Interpreted into normalized intents via the Vision Pipeline. Unrecognized signs gracefully trigger an "I didn't catch that" fallback.
- **AAC (Augmentative and Alternative Communication):** Maps visual AAC board selections into text/speech payloads for the Core Orchestrator.
- **Switch Access & Gestures:** Configurable mapped inputs with strict temporal validation to prevent accidental triggers.

## Cognitive Support
ASTRA's **AccessibilityProfileManager** dynamically adjusts verbosity, steps, and explanation depth based on user needs. A user can explicitly request, "Break this into steps," and the Task Planner will serialize the output accordingly.

## Hardware Abstraction
Accessibility is not tied to one device. A haptic output alert can route to a connected wrist wearable even if the task was initiated via voice on the Windows laptop.
