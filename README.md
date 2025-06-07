# Embroidery Categorizer

A Python CLI tool that automatically categorizes .PES embroidery files using AI.

## Features

- 📁 Reads all .PES files from a specified folder
- 🖼️ Converts .PES files to JPG images using pyembroidery
- 🤖 Uses OpenAI Vision API to analyze and categorize images
- 📂 Automatically creates folders for each category found
- 📋 Copies original .PES files to corresponding folders
- 🏗️ DDD/Clean Code architecture for easy maintenance and extension

## Architecture

The project follows Domain-Driven Design (DDD) principles with the following layers:

```
embroidery-categorizer/
├── domain/           # Entities, Value Objects, Repository Interfaces
├── infrastructure/   # Concrete implementations (OpenAI, File System)
├── application/      # Use Cases, Application Services
├── interfaces/       # CLI Interface
└── README.md
```

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure your OpenAI key:
```bash
export OPENAI_API_KEY="your-key-here"
```

Or create a `.env` file in the project root:
```
OPENAI_API_KEY=your-key-here
```

## Usage

### Basic command
```bash
python3 -m interfaces.cli categorize /path/to/pes/files
```

### Available options
```bash
python3 -m interfaces.cli categorize --help
```

### Examples
```bash
# Basic categorization with English folder names
python3 -m interfaces.cli categorize ./my_embroidery --output ./categorized_embroidery

# Create folders with Portuguese names
python3 -m interfaces.cli categorize ./my_embroidery --language pt-BR

# Dry run to preview what will be processed
python3 -m interfaces.cli categorize ./my_embroidery --dry-run
```

## Supported Categories

The AI can automatically identify and categorize:
- 🧸 Teddy Bears (ursinhos)
- 👼 Angels (anjos)
- 🏷️ Names/Text (nomes)
- 🚗 Cars (carrinhos)
- 🌸 Flowers (flores)
- 🦋 Animals (animais)
- ❤️ Hearts (corações)
- ⭐ Stars (estrelas)
- 🦋 Butterflies (borboletas)
- 👶 Babies (bebês)
- 🎄 Christmas (natal)
- 🐰 Easter (páscoa)
- ⚽ Sports (esportes)
- 🍎 Food (comida)
- 🌳 Nature (natureza)
- 📦 Other (outros)

## Language Support

The application supports folder names in multiple languages:

- **English (default)**: `--language en` or omit parameter
- **Portuguese**: `--language pt-BR`

Example folder structures:

**English**: `teddy_bears/`, `flowers/`, `angels/`, `cars/`  
**Portuguese**: `ursinhos/`, `flores/`, `anjos/`, `carrinhos/`

## Technical Architecture

### Domain Layer
- `EmbroideryFile`: Main entity representing an embroidery file
- `Category`: Value Object for categories
- `FilePath`: Value Object for file paths
- Repository and service interfaces

### Infrastructure Layer
- `OpenAICategorizationStrategy`: Implementation using OpenAI Vision API
- `FileSystemRepository`: File system management
- `PyEmbroideryConverter`: .PES to JPG conversion

### Application Layer
- `CategorizeFilesUseCase`: Main use case
- `CategorizationService`: Service orchestration
- Strategy Pattern for different AI providers

### Interface Layer
- CLI using Click framework for command-line interface

## Extensibility

To add new AI providers, simply implement the `CategorizationStrategy` interface:

```python
class NewProviderStrategy(CategorizationStrategy):
    def categorize_image(self, image_path: str) -> str:
        # Your implementation here
        pass
```

## Logs

The application generates detailed logs in `logs/embroidery_categorizer.log` for debugging and monitoring.

## Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License