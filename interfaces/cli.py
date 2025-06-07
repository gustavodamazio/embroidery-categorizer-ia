
"""
Command Line Interface for the embroidery categorizer.
"""
import os
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from application.use_cases import CategorizeFilesUseCase
from infrastructure.logging_config import setup_logging


# Load environment variables
load_dotenv()


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable detailed logging')
@click.option('--log-file', default='logs/embroidery_categorizer.log', 
              help='Log file (default: logs/embroidery_categorizer.log)')
@click.pass_context
def cli(ctx, verbose: bool, log_file: str):
    """
    🧵 Embroidery Categorizer - CLI tool for automatic categorization of .PES embroidery files
    
    This tool uses AI to automatically analyze and categorize your embroidery files,
    organizing them into folders by category (teddy bears, angels, names, cars, etc.).
    """
    # Configure logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level, log_file)
    
    # Ensure context exists
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['log_file'] = log_file


@cli.command()
@click.argument('input_directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--output', '-o', 'output_directory', type=click.Path(file_okay=False, dir_okay=True),
              help='Output directory for categorized files (default: INPUT_DIRECTORY/categorized)')
@click.option('--dry-run', is_flag=True, help='Simulate execution without copying files')
@click.option('--start-after', type=int, help='Start processing after specified process number (e.g., 500)')
@click.option('--language', '-l', type=click.Choice(['en', 'pt-BR']), default='en', 
              help='Language for folder names (default: en)')
@click.pass_context
def categorize(ctx, input_directory: str, output_directory: Optional[str], dry_run: bool, start_after: Optional[int], language: str):
    """
    Categorizes .PES files in a directory using AI.
    
    INPUT_DIRECTORY: Directory containing .PES files to categorize
    
    Examples:
    
        # Categorize files in current folder
        python -m embroidery_categorizer.interfaces.cli categorize ./my_embroidery
        
        # Specify output directory
        python -m embroidery_categorizer.interfaces.cli categorize ./embroidery -o ./categorized
        
        # Simulate execution without copying files
        python -m embroidery_categorizer.interfaces.cli categorize ./embroidery --dry-run
        
        # Start processing after file number 500
        python -m embroidery_categorizer.interfaces.cli categorize ./embroidery --start-after 500
        
        # Create folders with Portuguese names
        python -m embroidery_categorizer.interfaces.cli categorize ./embroidery --language pt-BR
    """
    logger.info("🧵 Starting Embroidery Categorizer")
    
    if dry_run:
        click.echo("🔍 Simulation mode enabled - no files will be copied")
        logger.info("Running in dry-run mode")
    
    if language == "pt-BR":
        click.echo("🇧🇷 Using Portuguese folder names")
        logger.info("Using pt-BR language for folder names")
    else:
        click.echo("🇺🇸 Using English folder names")
        logger.info("Using en language for folder names")
    
    # Validate configuration
    if not _validate_configuration():
        sys.exit(1)
    
    # Create use case
    try:
        use_case = CategorizeFilesUseCase()
        
        # Validate prerequisites
        validation = use_case.validate_prerequisites()
        if not all(validation.values()):
            click.echo("❌ Some prerequisites were not met:")
            for requirement, status in validation.items():
                status_icon = "✅" if status else "❌"
                click.echo(f"   {status_icon} {requirement}")
            sys.exit(1)
        
        click.echo("✅ All prerequisites met")
        
    except Exception as e:
        click.echo(f"❌ Error initializing application: {e}")
        logger.error(f"Initialization error: {e}")
        sys.exit(1)
    
    # Execute categorization
    try:
        click.echo(f"📂 Processing files in: {input_directory}")
        
        if not dry_run:
            results = use_case.execute(input_directory, output_directory, start_after, language)
            _display_results(results)
        else:
            click.echo("🔍 Simulation completed - use without --dry-run to process files")
            
    except KeyboardInterrupt:
        click.echo("\n⚠️ Operation cancelled by user")
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error during categorization: {e}")
        logger.error(f"Error during categorization: {e}")
        sys.exit(1)


@cli.command()
def check():
    """
    Checks if all dependencies and configurations are correct.
    """
    click.echo("🔍 Checking Embroidery Categorizer configuration...")
    
    all_ok = True
    
    # Check environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        click.echo("✅ OPENAI_API_KEY configured")
    else:
        click.echo("❌ OPENAI_API_KEY not found")
        click.echo("   Configure with: export OPENAI_API_KEY='your-key'")
        all_ok = False
    
    # Check dependencies
    dependencies = {
        "pyembroidery": "pyembroidery",
        "PIL (Pillow)": "PIL",
        "openai": "openai",
        "click": "click",
        "loguru": "loguru",
        "dotenv": "dotenv"
    }
    
    for name, module in dependencies.items():
        try:
            __import__(module)
            click.echo(f"✅ {name} installed")
        except ImportError:
            click.echo(f"❌ {name} not found")
            click.echo(f"   Install with: pip install {module}")
            all_ok = False
    
    # Test OpenAI connection (if configured)
    if openai_key:
        try:
            from infrastructure.openai_strategy import OpenAICategorizationStrategy
            strategy = OpenAICategorizationStrategy()
            if strategy.is_available():
                click.echo("✅ OpenAI connection working")
            else:
                click.echo("❌ Could not connect to OpenAI")
                all_ok = False
        except Exception as e:
            click.echo(f"❌ Error testing OpenAI: {e}")
            all_ok = False
    
    if all_ok:
        click.echo("\n🎉 Everything configured correctly!")
    else:
        click.echo("\n⚠️ Some configurations need to be fixed")
        sys.exit(1)


@cli.command()
@click.argument('pes_file', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--output', '-o', type=click.Path(file_okay=True, dir_okay=False),
              help='Output JPG file (default: same name with .jpg extension)')
def convert(pes_file: str, output: Optional[str]):
    """
    Converts a single .PES file to JPG.
    
    PES_FILE: .PES file to convert
    """
    from infrastructure.pyembroidery_converter import PyEmbroideryConverter
    from domain.value_objects import FilePath
    
    click.echo(f"🔄 Converting {pes_file} to JPG...")
    
    try:
        converter = PyEmbroideryConverter()
        
        input_path = FilePath.from_string(pes_file)
        
        if output is None:
            output = str(Path(pes_file).with_suffix('.jpg'))
        
        output_path = FilePath.from_string(output)
        
        success = converter.convert_pes_to_jpg(input_path, output_path)
        
        if success:
            click.echo(f"✅ Conversion completed: {output}")
        else:
            click.echo("❌ Conversion failed")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error during conversion: {e}")
        sys.exit(1)


def _validate_configuration() -> bool:
    """
    Validates basic application configuration.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        click.echo("❌ OPENAI_API_KEY not configured")
        click.echo("   Configure with: export OPENAI_API_KEY='your-key'")
        click.echo("   Or create .env file with: OPENAI_API_KEY=your-key")
        return False
    
    return True


def _display_results(results: dict) -> None:
    """
    Displays categorization results.
    """
    if results["success"]:
        click.echo("🎉 Categorization completed successfully!")
    else:
        click.echo("⚠️ Categorization completed with some issues")
    
    click.echo(f"\n📊 Results:")
    click.echo(f"   📁 Total files: {results['total_files']}")
    click.echo(f"   ✅ Processed: {results['processed_files']}")
    click.echo(f"   ❌ Failed: {results['failed_files']}")
    
    if results['categories_found']:
        click.echo(f"   🏷️ Categories found: {len(results['categories_found'])}")
        for category in sorted(results['categories_found']):
            click.echo(f"      - {category}")
    
    if results.get('output_directory'):
        click.echo(f"\n📂 Files organized in: {results['output_directory']}")
    
    if results['errors'] and results['failed_files'] > 0:
        click.echo(f"\n⚠️ Errors found:")
        for error in results['errors'][:3]:  # Show only first 3
            click.echo(f"   - {error}")
        if len(results['errors']) > 3:
            click.echo(f"   ... and {len(results['errors']) - 3} more errors (see log for details)")


if __name__ == '__main__':
    cli()
