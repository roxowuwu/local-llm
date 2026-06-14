# Bot.sh

Bot.sh is a Linux desktop assistant built to automate common tasks, interact with applications, and provide system-aware assistance through a combination of rules, intent recognition, memory, and optional LLM reasoning.

The goal of this project was not to create another chatbot. Instead, the focus was on building an assistant that can understand the user's device, interact with installed applications, perform system operations, remember previous interactions, and provide useful automation on a Linux machine.

---

## Why This Project Exists

Most AI assistants are good at conversation but cannot actually do anything on the user's computer.

Bot.sh was created to bridge that gap.

Instead of only answering questions, the assistant is designed to:

* Open applications
* Control media playback
* Search the web
* Read and write files
* Monitor storage usage
* Remember previous actions
* Understand the current system environment

The project follows a modular architecture so that each component can be developed and improved independently.

---

## Project Structure

```
bot_project/
│
├── main.py
│
├── config/
│   ├── user_prefs.yaml
│   ├── rules.yaml
│   └── system_snapshot.json
│
├── core/
│   ├── input_layer.py
│   ├── fast_path.py
│   ├── intent_router.py
│   ├── llm_brain.py
│   └── feedback.py
│
├── tools/
│   ├── __init__.py
│   ├── app_tools.py
│   ├── media_tools.py
│   ├── system_tools.py
│   ├── web_tools.py
│   ├── file_tools.py
│   └── storage_tools.py
│
├── memory/
│   ├── short_term.py
│   ├── long_term.py
│   └── long_term.db
│
├── system_scanner/
│   └── scanner.py
│
├── apis/
│   ├── spotify_api.py
│   └── weather_api.py
│
├── backups/
│   └── backup_manager.py
│
└── archive/
```

---

## How It Works

The assistant follows a pipeline-based architecture.

```
User Input
      ↓
Input Layer
      ↓
Fast Path Engine
      ↓
Intent Router
      ↓
LLM Brain (if required)
      ↓
Tool Executor
      ↓
Feedback Layer
      ↓
Memory System
```

Each layer has a specific responsibility.

---

## Input Layer

The Input Layer is responsible for collecting commands from the user.

Current support:

* Text input

Planned support:

* Voice input
* Wake-word activation

The rest of the system does not care whether the command came from a keyboard or microphone. Everything is converted into text before entering the pipeline.

---

## Fast Path Engine

The Fast Path Engine handles commands that are already known.

Example:

```
open youtube
```

Instead of sending this request to an LLM, the assistant immediately matches a rule and executes it.

This makes common commands extremely fast and avoids unnecessary model calls.

Rules are stored in:

```
config/rules.yaml
```

---

## Intent Router

Not every command matches a predefined rule.

The Intent Router attempts to classify the user's request into categories such as:

* Application control
* Media control
* File operations
* Web actions
* System actions
* General conversation

For simple commands, the router provides enough information for execution.

For more complicated requests, the router forwards the request to the LLM layer.

---

## LLM Brain

The LLM Brain is used when traditional rule matching and intent classification are not sufficient.

It receives:

* User input
* Conversation history
* Intent hints
* System context

The model then returns a structured action that the assistant can execute.

The goal is to use the LLM only when necessary instead of relying on it for every command.

---

## Tool System

The Tool System is where actions actually happen.

Each tool is responsible for a specific category of functionality.

### App Tools

Handles:

* Opening applications
* Closing applications
* Listing installed applications

### Media Tools

Handles:

* Playing music
* Pausing media
* Skipping tracks
* Volume control

### System Tools

Handles:

* Dark mode
* Wallpapers
* Brightness
* System information
* Trash management

### Web Tools

Handles:

* Opening URLs
* Search engine queries

### File Tools

Handles:

* Reading files
* Writing files
* Finding files

### Storage Tools

Handles:

* Disk usage reports
* Large file detection
* Duplicate file detection

---

## Memory System

The assistant uses two memory layers.

### Short-Term Memory

Stores recent conversation history.

Used for:

* Context awareness
* Follow-up questions
* Multi-turn conversations

### Long-Term Memory

Stored in SQLite.

Tracks:

* Previous actions
* User interactions
* Learned preferences

Examples:

* Preferred browser
* Preferred music application
* Frequently used programs

---

## System Scanner

The System Scanner allows the assistant to understand the machine it is running on.

It collects information such as:

* Operating system
* Hostname
* Installed applications
* Storage information
* Home directory size

The results are stored in:

```
config/system_snapshot.json
```

This snapshot provides context that helps the assistant make better decisions.

---

## Backup System

Whenever files are modified, backups can be created automatically.

Backups are stored separately so that changes can be reversed if needed.

This helps reduce the risk of accidental data loss.

---

## Design Philosophy

This project follows a simple principle:

> Reliability is more important than intelligence.

The assistant should always know what it can do, what it cannot do, and how to recover from failures.

Rather than relying entirely on AI models, the system combines:

* Rules
* Intent classification
* Tool execution
* Memory
* Optional LLM reasoning

This approach makes the assistant faster, cheaper, and more predictable.

---

## Current Status

Implemented:

* Modular architecture
* Rule-based execution
* Intent routing
* Tool execution framework
* Short-term memory
* Long-term memory
* System scanning
* Storage tools
* File tools

Planned:

* Voice input
* Wake-word activation
* Better planning and reasoning
* Preference learning
* Multi-step task execution
* More robust device discovery

---

## Future Direction

The long-term goal is to create a Linux assistant that can:

* Understand the system it runs on
* Learn user preferences
* Plan multi-step actions
* Execute tasks safely
* Operate through both text and voice

without becoming dependent on cloud services.

The project is being developed with a local-first mindset, giving users full control over their data and system access.
