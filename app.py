from flask import Flask, render_template, request, jsonify
import re

# --- Initialize the Flask App ---
app = Flask(__name__)

# --- Password Analysis Logic (Copied from your previous script) ---
MIN_LENGTH = 8
BREACHED_PASSWORDS = {
    "123456", "password", "123456789", "qwerty", "12345678", "111111",
    "12345", "iloveyou", "hunter2", "princess", "admin", "root", "welcome"
}

def assess_password(password: str) -> dict:
    score = 0
    feedback = {"suggestions": [], "warnings": []}
    if not password:
        return {"score": 0, "feedback": feedback}
    if password.lower() in BREACHED_PASSWORDS:
        feedback["warnings"].append("This password is in a data breach list and is very insecure.")
        return {"score": 0, "feedback": feedback}
    if len(password) < MIN_LENGTH:
        feedback["warnings"].append(f"Password should be at least {MIN_LENGTH} characters long.")
    else:
        score += min(len(password) * 2, 40)
    char_types = {"lower": r"[a-z]", "upper": r"[A-Z]", "digit": r"\d", "special": r"[\W_]"}
    types_found = sum(1 for pattern in char_types.values() if re.search(pattern, password))
    if types_found >= 3:
        score += types_found * 10
    if not re.search(char_types["lower"], password): feedback["suggestions"].append("Add lowercase letters.")
    if not re.search(char_types["upper"], password): feedback["suggestions"].append("Add uppercase letters.")
    if not re.search(char_types["digit"], password): feedback["suggestions"].append("Add numbers.")
    if not re.search(char_types["special"], password): feedback["suggestions"].append("Add special characters.")
    if re.search(r"(.)\1{2,}", password):
        score -= 15
        feedback["warnings"].append("Avoid repeating characters (e.g., 'aaa').")
    if any(seq in password.lower() for seq in ["abc", "123", "qwe", "asd"]):
        score -= 20
        feedback["warnings"].append("Avoid common keyboard sequences.")
    score = max(0, min(100, score))
    return {"score": int(score), "feedback": feedback}

def get_strength_from_score(score: int) -> str:
    if score <= 25: return "Very Weak"
    if score <= 50: return "Weak"
    if score <= 75: return "Moderate"
    if score <= 90: return "Strong"
    return "Very Strong"

# --- Define the Web Routes (URLs) ---

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/check-strength', methods=['POST'])
def check_strength():
    """API endpoint to check the password strength."""
    password = request.json.get('password', '')
    assessment = assess_password(password)
    strength = get_strength_from_score(assessment['score'])
    
    # Return the analysis as a JSON object
    return jsonify({
        'score': assessment['score'],
        'strength': strength,
        'feedback': assessment['feedback']
    })

if __name__ == '__main__':
    # This allows you to run the app locally for testing
    app.run(debug=True)
