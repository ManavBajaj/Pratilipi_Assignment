# Adaptive Taxonomy Mapper

This repository contains a system for automatically classifying story descriptions into a predefined genre taxonomy. It utilizes a two-stage process involving an LLM for semantic signal extraction and a rule-based adjudicator for final classification. The entire system is presented through an interactive Streamlit web application.

## How it Works

The classification process is broken down into two main stages:

1.  **Signal Extraction (`extractor.py`):**
    *   The story description and user-provided tags are sent to an LLM (via the Groq API for speed and reliability).
    *   The LLM is prompted to extract key semantic "signals" from the text and return them in a structured JSON format. These signals include `primary_theme`, `relationship_dynamic`, `thriller_type`, etc.
    *   If the LLM call fails or returns an invalid format, a robust heuristic-based fallback function (`heuristic_fallback`) performs pattern matching to generate the signals.

2.  **Adjudication (`adjudicator.py`):**
    *   The extracted signals are fed into the `decide_subgenre` function.
    *   This function uses a set of weighted rules to map the combination of signals to the most appropriate subgenre defined in `taxonomy.json`.
    *   It handles ambiguous cases, identifies unmappable content (like instructional text), and provides a clear reasoning for its final decision.

## Features

*   **LLM-Powered Analysis:** Leverages the Groq API with Llama 3.1 for fast and accurate semantic analysis of story text.
*   **Robust Fallback:** Includes a keyword-based heuristic fallback to ensure the system works even if the LLM API is unavailable.
*   **Rule-Based Adjudication:** A transparent, rule-based system makes the final classification, providing clear reasoning for each decision.
*   **Interactive UI:** A Streamlit application provides an easy-to-use interface for mapping stories, viewing results, and running test cases.
*   **Batch Testing:** Allows running a suite of predefined "golden" test cases to validate system accuracy.
*   **Session Management:** Results from a session are stored and can be downloaded as a single JSON file.

## File Structure

*   `main.py`: The entry point for the Streamlit web application. It handles the UI, state management, and orchestrates the calls to the extractor and adjudicator.
*   `extractor.py`: Contains the logic for extracting semantic signals from text using an LLM API (Groq) and the heuristic fallback mechanism.
*   `adjudicator.py`: Implements the rule-based logic to map the extracted signals to a final subgenre based on the defined taxonomy.
*   `taxonomy.json`: A JSON file defining the hierarchical genre taxonomy the system classifies against.
*   `test_cases.json`: Contains a set of 10 test cases with stories, tags, and expected outcomes, used for validating the system.


## Live Demo
The working application can be accessed here:
https://pratilipiassignmentgit-2025.streamlit.app/

## Setup and Usage

### Prerequisites

*   Python 3.7+
*   A free API key from [Groq](https://console.groq.com/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/manavbajaj/pratilipi_assignment.git
    cd pratilipi_assignment
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install streamlit requests
    ```

### Running the Application

1.  **Start the Streamlit app:**
    ```bash
    streamlit run main.py
    ```

2.  **Use the Web Interface:**
    *   Open your browser to the local URL provided by Streamlit.
    *   On the sidebar, enter your Groq API Key.
    *   Navigate to the "Map Story" tab.
    *   Enter a story description and optional tags.
    *   Click "Map to Taxonomy" to see the classification result, reasoning, and extracted signals.
    *   Go to the "Test Cases" tab to run the automated tests against `test_cases.json` and see the accuracy score.
    *   The "Session Results" tab aggregates all classifications made during your current session.

## Taxonomy Definition

The system classifies stories into the following structure defined in `taxonomy.json`:

```json
{
  "Fiction": {
    "Romance": ["Slow-burn", "Enemies-to-Lovers", "Second Chance"],
    "Thriller": ["Espionage", "Psychological", "Legal Thriller"],
    "Sci-Fi": ["Hard Sci-Fi", "Space Opera", "Cyberpunk"],
    "Horror": ["Psychological Horror", "Gothic", "Slasher"]
  }
}


