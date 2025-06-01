# mas-process-discovery

This is the accompanying repository for the Master Thesis, containing all data and analysis code for multi-agent system process discovery experiments.

## Repository Structure

This repository includes:
- Results of the experiments
- Analysis code for data processing
- Chart generation scripts
- Statistical summaries and failure analysis

## Naming Convention

Each experimental run follows this naming pattern:
```
[LLM]_[Process]_[Setup]
```

### LLM Models
- `GeminiPro`
- `Mistral`
- `Deepseek`

### Process Types
- `Shop`
- `Reimbursement`
- `Hotel`

### Setup Configurations
- `Monolithic`
- `Duo`
- `Manager`
- `Team`

## Data Structure

For each experimental run, you'll find:

### Core Data
- **JSON trace** - Complete execution log from mlflow
- **`artifacts/conversation.txt`** - Human-readable summary of the conversation

### Generated Artifacts
- **`artifacts/`** folder containing all generated files, like the process models as well as the failure analysis

### Statistics
- **Agent-level metrics**:
  - Prompt tokens used
  - Completion tokens generated
  - Number of invocations
