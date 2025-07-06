# Classic Operating System Problems in Python

This repository contains Python implementations of three classic concurrency problems studied in Operating Systems:

- 🍽️ **Dining Philosophers Problem**
- 📖 **Readers-Writers Problem**
- 🛠️ **Producer-Consumer Problem**

These problems are commonly used to illustrate synchronization issues and solutions in multithreaded environments.

## Technologies Used

- **Python 3**
- **`threading`** module for managing concurrent execution
- **`Lock`, `Semaphore`, and `Condition`** for synchronization mechanisms

## Implemented Problems

### 1. Dining Philosophers Problem
Simulates a group of philosophers sitting around a table, alternating between thinking and eating. The implementation ensures that no philosopher starves and that deadlock is avoided through proper use of locks or semaphores.

### 2. Readers-Writers Problem
Models a shared resource (e.g., a database) accessed by multiple reader and writer threads. The implementation prioritizes either readers or writers (depending on the version) and handles synchronization to avoid race conditions.

### 3. Producer-Consumer Problem
Demonstrates how producers add items to a shared buffer while consumers remove them. This implementation ensures that the buffer does not overflow or underflow, using conditions or semaphores to synchronize access.

## Key Concepts

- 🔒 Mutual Exclusion
- 🕒 Synchronization
- ⚠️ Deadlock Prevention
- 🌀 Thread Coordination

## Notes

- Each problem is implemented in a separate Python script.
- The focus is on demonstrating correct synchronization logic rather than UI or external libraries.
- Suitable for academic study, simulation, and experimentation.


