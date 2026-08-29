# ASTRA 2.0 Architecture

ASTRA 2.0 is built on a highly modular, decoupled architecture centered around the `CoreOrchestrator` and `TaskManager`.

## Core Components
- **Core Orchestrator:** The brain of the operation. It receives normalized intents (whether from Voice, Sign Language, or AAC) and delegates them to the Task Planner.
- **Task Planner:** Implements a GOAL -> PLAN -> EXECUTE loop, breaking complex goals into multi-step execution plans across specialized agents.
- **Capability Manager:** The hardware abstraction layer. Instead of tightly coupling to a phone camera, agents request a `CAMERA` capability, and the manager dynamically routes the request to the highest-priority connected device (e.g., Smart Glasses > Phone > Laptop), supporting seamless mid-task fallbacks.
- **Conversation Turn Manager:** Ensures that across all devices and modalities, ASTRA maintains a strict state machine (`LISTENING` -> `PROCESSING` -> `EXECUTING` -> `SPEAKING` -> `WAITING_FOR_USER`) to prevent duplicate speech and conversational collisions.

## AI Routing
The `ModelRouter` dynamically routes requests based on task complexity, required capabilities (like vision/coding), and network availability. Simple tasks stay on the local LLM to preserve privacy and reduce latency.

## Memory
The `MemoryManager` segregates context:
- **Working Memory:** Cleared after every discrete task to prevent context leakage.
- **Session Memory:** Persists during the active conversation.
- **Preference Memory:** Stores long-term user settings.
