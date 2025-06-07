# Usage Examples - Embroidery Categorizer

## Initial Setup

1. **Configure your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-openai-key-here"
```

Or create a `.env` file:
```bash
cp .env.example .env
# Edit the .env file and add your key
```

2. **Check if everything is configured:**
```bash
python3 -m interfaces.cli check
```

## Available Commands

### 1. Categorize .PES Files

**Basic command:**
```bash
python3 -m interfaces.cli categorize /path/to/pes/folder
```

**With custom output directory:**
```bash
python3 -m interfaces.cli categorize ./my_embroidery --output ./categorized_embroidery
```

**Simulation mode (doesn't copy files):**
```bash
python3 -m interfaces.cli categorize ./embroidery --dry-run
```

**With detailed logs:**
```bash
python3 -m interfaces.cli --verbose categorize ./embroidery
```

**With Portuguese folder names:**
```bash
python3 -m interfaces.cli categorize ./embroidery --language pt-BR
```

**With English folder names (default):**
```bash
python3 -m interfaces.cli categorize ./embroidery --language en
```

**Start processing from specific file number:**
```bash
python3 -m interfaces.cli categorize ./embroidery --start-after 500
```

### 2. Convert a .PES File to JPG

```bash
python3 -m interfaces.cli convert file.pes
```

**With specific output file:**
```bash
python3 -m interfaces.cli convert file.pes --output image.jpg
```

### 3. Check Configuration

```bash
python3 -m interfaces.cli check
```

## Output Structure

After categorization, files will be organized as follows:

### English Folders (default or --language en)
```
categorized_embroidery/
├── teddy_bears/
│   ├── bear1.pes
│   ├── bear1.jpg
│   └── bear2.pes
├── angels/
│   ├── angel1.pes
│   ├── angel1.jpg
│   └── angel2.pes
├── names/
│   ├── name1.pes
│   └── name2.pes
└── flowers/
    ├── flower1.pes
    ├── flower1.jpg
    └── flower2.pes
```

### Portuguese Folders (--language pt-BR)
```
categorized_embroidery/
├── ursinhos/
│   ├── bear1.pes
│   ├── bear1.jpg
│   └── bear2.pes
├── anjos/
│   ├── angel1.pes
│   ├── angel1.jpg
│   └── angel2.pes
├── nomes/
│   ├── name1.pes
│   └── name2.pes
└── flores/
    ├── flower1.pes
    ├── flower1.jpg
    └── flower2.pes
```

## Supported Categories

The AI can automatically identify:

### English Categories (--language en)
- 🧸 **teddy_bears** - Teddy bears, bears
- 👼 **angels** - Angels
- 🏷️ **names** - Names, text, letters
- 🚗 **cars** - Cars, vehicles
- 🌸 **flowers** - Flowers, floral, plants
- 🦋 **animals** - Animals, pets
- ❤️ **hearts** - Hearts, love
- ⭐ **stars** - Stars
- 🦋 **butterflies** - Butterflies
- 👶 **babies** - Babies, children
- 🎄 **christmas** - Christmas, holiday
- 🐰 **easter** - Easter, bunny
- ⚽ **sports** - Sports, football, etc.
- 🍎 **food** - Food, fruits, etc.
- 🌳 **nature** - Nature, trees
- 📦 **other** - Other, unidentified

### Portuguese Categories (--language pt-BR)
- 🧸 **ursinhos** - Teddy bears, ursos
- 👼 **anjos** - Angels, anjos
- 🏷️ **nomes** - Names, text, letras
- 🚗 **carrinhos** - Cars, vehicles, carros
- 🌸 **flores** - Flowers, floral, plantas
- 🦋 **animais** - Animals, pets, bichos
- ❤️ **coracoes** - Hearts, love, amor
- ⭐ **estrelas** - Stars, estrelas
- 🦋 **borboletas** - Butterflies
- 👶 **bebes** - Babies, children, crianças
- 🎄 **natal** - Christmas, holiday, noel
- 🐰 **pascoa** - Easter, coelho
- ⚽ **esportes** - Sports, futebol, etc.
- 🍎 **comida** - Food, frutas, etc.
- 🌳 **natureza** - Nature, trees, árvores
- 📦 **outros** - Other, não identificado

## Logs

Logs are saved in `logs/embroidery_categorizer.log` and include:
- Processed files
- Identified categories
- Errors encountered
- Processing statistics

## Troubleshooting

### Error: "OpenAI API key not found"
Configure your OpenAI key as shown above.

### Error: "Could not connect to OpenAI"
Check your internet connection and verify your API key is correct.

### Error: ".PES file cannot be converted"
Some .PES files may be corrupted or in an unsupported format.

### Performance
- Use `--dry-run` first to see how many files will be processed
- Conversion and categorization may take a few seconds per file
- Larger files take longer to process

## Complete Example

```bash
# 1. Configure API key
export OPENAI_API_KEY="sk-..."

# 2. Check configuration
python3 -m interfaces.cli check

# 3. Test with one file first
python3 -m interfaces.cli convert example.pes

# 4. Simulate categorization
python3 -m interfaces.cli categorize ./my_embroidery --dry-run

# 5. Run actual categorization with English folders
python3 -m interfaces.cli categorize ./my_embroidery --output ./organized

# 6. Run categorization with Portuguese folders
python3 -m interfaces.cli categorize ./my_embroidery --output ./organizados --language pt-BR

# 7. Check logs
cat logs/embroidery_categorizer.log
```

## Language Feature Examples

```bash
# English folders (default)
python3 -m interfaces.cli categorize ./embroidery
# Creates: teddy_bears/, flowers/, angels/, etc.

# Portuguese folders
python3 -m interfaces.cli categorize ./embroidery --language pt-BR
# Creates: ursinhos/, flores/, anjos/, etc.

# Short form
python3 -m interfaces.cli categorize ./embroidery -l pt-BR

# Combined with other options
python3 -m interfaces.cli categorize ./embroidery -l pt-BR --output ./organizados --verbose
```

## Advanced Usage

```bash
# Process large batches with restart capability
python3 -m interfaces.cli categorize ./large_collection --start-after 1000

# Verbose logging with Portuguese folders
python3 -m interfaces.cli -v categorize ./embroidery -l pt-BR -o ./resultado

# Test mode with specific language
python3 -m interfaces.cli categorize ./test_files --dry-run --language pt-BR
```