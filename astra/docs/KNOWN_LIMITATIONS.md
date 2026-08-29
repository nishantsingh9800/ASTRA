# ASTRA 2.0 Known Limitations

ASTRA is committed to absolute truthfulness. The following limitations exist in the current Release Candidate:

1. **Hardware Adapters:** The Smart Glasses and Wearable adapters currently operate via simulated data contracts. Physical Bluetooth/Wifi integration is flagged as `HARDWARE_INTEGRATION_PENDING`.
2. **Offline Complex Reasoning:** While the local LLM handles basic tool execution and natural language parsing offline, complex autonomous tasks (e.g., multi-step research compilation) require the Cloud Model for acceptable reliability.
3. **Android Capabilities:** Android integration shares the core conversational state and task lifecycle, but deep OS-level UI automation is restricted compared to the native Windows accessibility hooks.
4. **Agent Sandboxing:** The Self-Improvement Engine currently relies on mocked integration test payloads. A full Docker/sandbox container is required before unconstrained LLM-generated code can be executed safely during the isolated build phase.
5. **Sign Language Vocabulary:** The local vision pipeline supports a constrained set of core navigational/command signs. Edge-case vocabulary will gracefully fall back to the "I didn't catch that sign clearly" response.
