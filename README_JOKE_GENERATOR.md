# Random Joke Generator 🤣

A Python application that fetches random jokes from the [JokeAPI](https://jokeapi.dev/) external API.

## Features

- ✅ Fetch random jokes from an external API
- ✅ Support for multiple joke types (Single, Two-part)
- ✅ Filter by joke category (General, Programming, Knock-knock, etc.)
- ✅ Safe mode to exclude inappropriate content
- ✅ Fetch multiple jokes at once
- ✅ Clean, formatted output

## Installation

1. Clone or download this project
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the main script to get random jokes:

```bash
python joke_generator.py
```

### Using as a Module

```python
from joke_generator import JokeGenerator

# Create an instance
generator = JokeGenerator()

# Get a random joke
joke = generator.get_random_joke()
generator.display_joke(joke)

# Get a programming joke
prog_joke = generator.get_random_joke(joke_type="Programming")
generator.display_joke(prog_joke)

# Get multiple jokes
jokes = generator.get_multiple_jokes(count=5)
for joke in jokes:
    generator.display_joke(joke)
```

## API Parameters

### `get_random_joke(joke_type, safe_mode)`

- **joke_type** (str): Type of joke
  - `"Any"` - Random joke (default)
  - `"Single"` - Single-line jokes
  - `"Twopart"` - Two-part jokes (setup + delivery)
  - `"General"` - General jokes
  - `"Programming"` - Programming jokes
  - `"Knock-knock"` - Knock-knock jokes

- **safe_mode** (bool): If `True`, only family-friendly jokes are returned (default: `True`)

## Supported Joke Categories

- General
- Knock-knock
- Programming
- Science
- Math
- Dark
- Spooky
- Pun

## Example Output

```
==================================================
📝 JOKE OF THE DAY 📝
==================================================

Why do programmers prefer dark mode?

Because light attracts bugs!

Category: Programming
==================================================
```

## API Used

This project uses the **JokeAPI** by Sv443:
- Website: https://jokeapi.dev/
- Documentation: https://jokeapi.dev/docs
- No authentication required
- Free to use

## Error Handling

The application includes error handling for:
- Network connectivity issues
- API timeouts
- Invalid responses
- JSON parsing errors

## Requirements

- Python 3.7+
- requests library (see `requirements.txt`)

## License

This project is open source and free to use.

## Contributing

Feel free to enhance this joke generator by:
- Adding new features
- Improving error handling
- Adding more joke categories
- Creating a web interface

Enjoy the jokes! 😄
