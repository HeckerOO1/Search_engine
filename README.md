# Emergency Search Engine

An AI-powered search engine with emergency detection capabilities.

## Prerequisites

- Python 3.8+
- pip

## Quick Start

1.  **Setup Environment Variables**:
    Ensure you have a `.env` file in the `model` directory. You can copy the example:
    ```bash
    cp model/.env.example model/.env
    ```
    Edit `model/.env` to add your `GEMINI_API_KEY` if you want to use the AI Truth Filter.

2.  **Run the Application**:
    We have provided a convenience script to install dependencies and start the server.
    ```bash
    ./run_dev.sh
    ```
    
    Or manually:
    ```bash
    pip install -r model/requirements.txt
    python model/app.py
    ```

3.  **Access**:
    Open [http://localhost:5000](http://localhost:5000) in your browser.

## Features

- **Emergency Mode**: Detects urgent queries and re-ranks results for safety and speed.
- **Truth Filter**: Uses Gemini AI to score reliability of content.
- **Spell Checker**: Custom Levenshtein-based spell correction.
