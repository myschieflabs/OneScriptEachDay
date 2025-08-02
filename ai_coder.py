import pyautogui
import google.generativeai as genai
from PIL import Image
import io
import pyperclip
import re
import os
import sys
import time
import subprocess
import requests
import json

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set!")
    print("Please set your API key: export GEMINI_API_KEY='your-api-key-here'")
    sys.exit(1)

MODEL = 'gemini-1.5-flash'
OLLAMA_MODEL = "codellama:latest"

def take_screenshot():
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None

def detect_language(code_snippet):
    if re.search(r'#include\s+<.*?>', code_snippet):
        return 'cpp'
    elif re.search(r'import\s+\w+', code_snippet):
        return 'python' if 'def ' in code_snippet else 'java'
    elif re.search(r'function\s+\w+', code_snippet):
        return 'javascript'
    elif re.search(r'public\s+class', code_snippet):
        return 'java'
    return 'text'

def get_code_from_gemini(img_bytes):
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL)

        image = Image.open(io.BytesIO(img_bytes))

        response = model.generate_content([
            "This is a coding problem. Carefully understand it and generate the complete and error-free solution in the detected language based on the syntax. Do not use placeholders. Ensure it compiles without errors. Don't include any comments, markdown, or extra text.",
            image
        ])
        return response.text
    except Exception as e:
        print(f"Gemini failed, trying Ollama... ({e})")
        return None

def get_code_from_ollama(img_bytes):
    try:
        prompt = "Extract the problem from this image and solve it using correct syntax in the language you detect (C++, Python, Java, etc). Return only the code. Do not explain. Make sure the code is clean and free from errors. No markdown, no comments."
        base64_img = base64.b64encode(img_bytes).decode('utf-8')
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "images": [base64_img],
            "stream": False
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.ok:
            return response.json().get("response", "")
        else:
            print(f"❌ Ollama error: {response.text}")
            return None
    except Exception as e:
        print(f"Ollama failed: {e}")
        return None

def extract_code(response_text):
    if not response_text:
        return None

    patterns = [
        r"```(?:cpp|c\+\+|python|java|js)?\n(.*?)```",
        r"```\n(.*?)```",
        r"`(.*?)`",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, response_text, re.DOTALL)
        if matches:
            return matches[0].strip()

    lines = response_text.split('\n')
    return '\n'.join([line.strip() for line in lines if not line.strip().startswith('```')])

def clean_solution_wrappers(code):
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        if re.search(r'(Solution\s*\(\)|\w+\s*\(\)).*\w+\s*\(', line):
            continue
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def type_code_at_cursor(code):
    try:
        cleaned_code = clean_solution_wrappers(code)
        pyautogui.alert("Place your cursor where you want the code to be typed, then click OK. You will have 5 seconds after clicking OK.", "Coding Solver: Place Cursor")
        time.sleep(5)
        pyautogui.typewrite(cleaned_code)
        print("Code typed at cursor position!")
        return True
    except Exception as e:
        print(f"❌ Error typing code: {e}")
        return False

def main():
    print("Coding Problem Solver (Multi-Language, Gemini + Ollama)")
    img_bytes = take_screenshot()
    if not img_bytes:
        return

    response = get_code_from_gemini(img_bytes)
    if not response:
        response = get_code_from_ollama(img_bytes)
    if not response:
        print("Both Gemini and Ollama failed to return a valid response.")
        return

    code = extract_code(response)
    if not code:
        print("Failed to extract code from response.")
        return

    lang = detect_language(code)
    print(f"Detected Language: {lang}")
    print("Final Extracted Code:\n" + code[:500] + ("..." if len(code) > 500 else ""))

    type_code_at_cursor(code)

if __name__ == "__main__":
    main()
