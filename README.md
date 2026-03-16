# myQuickFolderTagger

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![Made with uv](https://img.shields.io/badge/Made%20with-uv-1f425f.svg)](https://github.com/astral-sh/uv)

A locally-run, cross-platform CLI tool that reads a target codebase's `README.md` and uses an LLM to assign a 1-3 word tag describing what the codebase does. Results are stored in a configurable CSV file with thread-safe writing.

## Features

- **Zero Telemetry**: Completely local execution; your codebase never leaves your machine unless you configure a cloud LLM provider.
- **Cross-Platform**: Works on Windows, Linux, and macOS.
- **Configurable Storage**: Writes tags and tech stacks to a configurable CSV index with thread safety.
- **Multi-Provider Support**: Supports OpenAI, Anthropic, Google Gemini, OpenRouter, Ollama, and LM Studio.
- **Case-Insensitive README Detection**: Automatically looks for README.md, readme.md, or Readme.md.
- **Thread-Safe CSV Writing**: Uses file locking to prevent corruption when multiple instances run simultaneously.

## Setup

It is recommended to use `uv` for dependency management:

```bash
uv sync
```

Alternatively, use standard `pip` with the pyproject.toml file:

```bash
pip install .
```

Or install dependencies manually:
- requests>=2.32.5
- openai>=2.28.0
- anthropic>=0.84.0
- google-genai>=1.67.0

## Usage

```bash
uv run tagger.py --path <path_to_codebase_1> [path_2 ...] --provider <provider_name> --model <model_name>
```

### Examples

**Google Gemini (Requires `GEMINI_API_KEY` or `GEMINI_2_5_FLASH_API_KEY`)**
```bash
uv run tagger.py --path ../my-cool-project --provider google --model gemini-2.5-flash
```

**Local Ollama (Requires Ollama running locally, no API key)**
```bash
uv run tagger.py --path ../my-cool-project --provider ollama --model llama3
```

**Batch / Recursive Scanning**
Scan a folder containing multiple repositories:
```bash
uv run tagger.py --path ../Coding/Repos --recursive --provider openai --model gpt-4o
```

**OpenAI (Requires `OPENAI_API_KEY`)**
```bash
uv run tagger.py --path ../my-cool-project --provider openai --model gpt-4o
```

**Anthropic (Requires `ANTHROPIC_API_KEY`)**
```bash
uv run tagger.py --path ../my-cool-project --provider anthropic --model claude-3-5-sonnet-20241022
```

### Options

- `--path`: (Required) One or more paths to the codebases you want to analyze.
- `--recursive`: (Optional) If set, the tool will recursively search all provided paths for any subdirectories containing a `README.md` and process them. Automatically skips common ignore folders like `node_modules`, `.venv`, etc.
- `--provider`: (Required) One of `openai`, `anthropic`, `google`, `openrouter`, `ollama`, `lmstudio`.
- `--model`: (Required) The LLM model name (e.g. gpt-4o, gemini-2.5-flash, llama3).
- `--csv-path`: (Optional) The absolute or relative path to the CSV file where the tags will be saved. Defaults to `codebase_tags.csv` in the current directory.

### Output Format

The tool creates or appends to a CSV file with the following columns:
- `Codebase Path`: Absolute path to the analyzed codebase
- `Tag`: 1-3 word description of what the codebase does
- `Tech Stack`: Comma-separated list of technologies detected (if any)

Example CSV output:
```
Codebase Path,Tag,Tech Stack
/home/user/projects/my-cool-project,web scraping,Python, BeautifulSoup
/home/user/projects/api-service,REST API,Node.js, Express
```

## Environment Variables

### API Keys
The application dynamically searches for API keys based on the Model or the Provider.
For example, if you run with `--provider google --model gemini-2.5-flash`:
1. It looks for `GEMINI_2_5_FLASH_API_KEY`
2. Then it looks for `GEMINI_API_KEY`
3. Then it looks for `GOOGLE_API_KEY`

This pattern applies to all cloud providers (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY`).

### Other Config
- `TAGGER_CSV_PATH`: Defines the unified path to the CSV file so you don't need to specify `--csv-path` every time.
- `OLLAMA_HOST`: Set to your Ollama API endpoint (Default: `http://localhost:11434`)
- `LMSTUDIO_HOST`: Set to your LM Studio endpoint (Default: `http://localhost:1234/v1`)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and follow the existing code style.

## Security

This tool is designed to run completely locally by default. No data is sent to external services unless you explicitly configure a cloud LLM provider. When using cloud providers, only the README content is sent to the provider's API for analysis.

## Contact

For questions or support, please open an issue in the GitHub repository.