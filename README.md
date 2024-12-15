# Automated Quiz Checking Script

This script uses Google's Gemini API to analyze images of test papers and extract answers, including multiple-choice selections and true/false responses. It outputs the results in JSON and human-readable text formats.

## Installation

1. **Python and Pip:**
   - Ensure you have Python 3.12 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).
   - Pip (the Python package installer) is usually included with Python.

2. **Virtual Environment (Recommended):**
   - It's best practice to create a virtual environment for your project. This isolates the dependencies for your project from other Python projects.
   - Open a terminal or command prompt and run:
      ```bash
      python -m venv venv
      ```
   - Activate the virtual environment:
     - On macOS and Linux:
       ```bash
       source venv/bin/activate
       ```
     - On Windows:
       ```bash
       venv\Scripts\activate
       ```

3. **Install Dependencies:**
   - Install the required Python libraries using pip:
     ```bash
     pip install -r requirements.txt
     ```

4. **Google Gemini API Key:**
   - You will need an API key to use Google's Gemini API. You can obtain one from [Google AI Studio](https://ai.google.dev/).
   - **Set up .env file:**
     - Create a file named `.env` in the same directory as your script.
     - Add your API key to the `.env` file:
        ```
        GOOGLE_API_KEY=YOUR_API_KEY_HERE
        ```
       **Replace `YOUR_API_KEY_HERE` with your actual API key.**

## Usage

1.  **Run the Script:**
    - From your terminal/command prompt, navigate to the directory containing the script and run:
        ```bash
        python scanner.py
        ```

2.  **Select Input Files:**
    - A file dialog window will appear.
    - Select one or more student response files (`.png` or `.jpg` files)
    - **Important:** The script is primarily designed to process image files (`.png` or `.jpg`).
  

3.  **Output Files:**
    - Once processing is complete, the script will create two files in the same directory:
        - `output.json`:  A JSON file containing the structured output of the analysis, including questions, detected answers, bounding boxes for options (if applicable), and more.
        - `output.txt`: A human-readable text file containing the extracted questions and answers.

## Debugging

Set `DEBUG = 1` in `scanner.py` for printing debug information.

## Understanding the output

### output.json

- Contains a JSON formatted list where each element is a dictionary, representing a question and its properties
    - `question_number`: the number of the question
    - `question_contents`: the text contents of the question
    - `question_type`: a string stating whether the question is "Multiple Choice" or "True/False"
    - `boolean_answer` (only present if `question_type` is "True/False"): an enum string of `"True"`, `"False"`, `"Unanswered"`, or `"Unknown"`. 
    - `options` (only present if `question_type` is "Multiple Choice"): an array of dictionaries representing the options:
        - `option_contents`: a string containing the text of the option
        - `option_state`: a string describing the option's state, one of `"Ticked"`, `"Crossed"`, `"Filled"`, `"Circled"`, `"Empty"`, or `"Unknown"`
        - `bounding_box`: an array of floats representing the top left and bottom right coordinates of the bounding box, in the format `[ymin, xmin, ymax, xmax]`

### output.txt
- Contains the same information, but in a human-readable format
