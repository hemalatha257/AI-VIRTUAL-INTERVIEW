from flask import Flask, render_template_string, request, jsonify
import random
import cv2
import base64
import numpy as np
from textblob import TextBlob

app = Flask(__name__)


# =========================================================
# QUESTIONS DATABASE
# =========================================================

questions = {

    "developer": [
        {
            "q": "Explain OOP concepts.",
            "keywords": ["class", "object", "inheritance", "polymorphism"]
        },
        {
            "q": "What is a database index?",
            "keywords": ["search", "speed", "performance"]
        },
        {
            "q": "Difference between stack and queue.",
            "keywords": ["LIFO", "FIFO"]
        },
        {
            "q": "What is REST API?",
            "keywords": ["http", "stateless", "request"]
        },
        {
            "q": "Explain recursion.",
            "keywords": ["function", "calls", "base case"]
        },
        {
            "q": "What is multithreading?",
            "keywords": ["threads", "parallel", "concurrent"]
        },
        {
            "q": "Explain normalization in DBMS.",
            "keywords": ["normal form", "redundancy", "dependency"]
        },
        {
            "q": "What is Big-O notation?",
            "keywords": ["complexity", "time", "space"]
        },
        {
            "q": "Difference between process and thread.",
            "keywords": ["memory", "execution", "cpu"]
        },
        {
            "q": "What is Git and why is it used?",
            "keywords": ["version control", "repository", "commit"]
        },
        {
            "q": "Explain MVC architecture.",
            "keywords": ["model", "view", "controller"]
        },
        {
            "q": "What is a deadlock?",
            "keywords": ["resource", "blocked", "waiting"]
        },
        {
            "q": "Explain cloud computing.",
            "keywords": ["aws", "azure", "scalable"]
        },
        {
            "q": "What is Docker?",
            "keywords": ["container", "deployment", "image"]
        },
        {
            "q": "Explain difference between SQL and NoSQL.",
            "keywords": ["relational", "schema", "document"]
        }
    ],

    "hr": [
        {
            "q": "Tell me about yourself.",
            "keywords": ["background", "skills", "experience"]
        },
        {
            "q": "Why should we hire you?",
            "keywords": ["value", "team", "contribution"]
        },
        {
            "q": "Describe your strengths.",
            "keywords": ["hardworking", "adaptable", "leadership"]
        },
        {
            "q": "Describe your weakness.",
            "keywords": ["improve", "learning", "growth"]
        },
        {
            "q": "How do you handle stress?",
            "keywords": ["calm", "focus", "prioritize"]
        },
        {
            "q": "Describe a conflict you resolved.",
            "keywords": ["communication", "solution", "team"]
        },
        {
            "q": "Where do you see yourself in 5 years?",
            "keywords": ["career", "growth", "goal"]
        },
        {
            "q": "Why do you want this role?",
            "keywords": ["interest", "company", "fit"]
        },
        {
            "q": "Describe leadership.",
            "keywords": ["guide", "motivate", "team"]
        },
        {
            "q": "How do you manage deadlines?",
            "keywords": ["planning", "priority", "time"]
        },
        {
            "q": "Tell me about a failure.",
            "keywords": ["learn", "mistake", "improve"]
        },
        {
            "q": "How do you work in a team?",
            "keywords": ["collaboration", "support", "communication"]
        }
    ],

    "general": [
        {
            "q": "What motivates you?",
            "keywords": ["goal", "passion", "achievement"]
        },
        {
            "q": "Describe teamwork.",
            "keywords": ["collaboration", "support", "communication"]
        },
        {
            "q": "What is success to you?",
            "keywords": ["achieve", "goal", "growth"]
        },
        {
            "q": "How do you learn new skills?",
            "keywords": ["practice", "research", "improve"]
        },
        {
            "q": "What is leadership?",
            "keywords": ["guide", "inspire", "team"]
        },
        {
            "q": "How do you handle criticism?",
            "keywords": ["feedback", "improve", "learn"]
        },
        {
            "q": "Describe problem-solving approach.",
            "keywords": ["analyze", "solution", "logic"]
        },
        {
            "q": "Why is communication important?",
            "keywords": ["clarity", "understanding", "team"]
        },
        {
            "q": "What is innovation?",
            "keywords": ["creative", "new idea", "improvement"]
        },
        {
            "q": "What are your career goals?",
            "keywords": ["future", "growth", "development"]
        }
    ]
}


# =========================================================
# ANSWER ANALYSIS
# =========================================================

def analyze_answer(answer, keywords):

    score = 0

    answer_lower = answer.lower()

    # Keyword score
    keyword_hits = sum(
        1 for keyword in keywords
        if keyword.lower() in answer_lower
    )

    keyword_score = keyword_hits * 20

    # Answer length score
    word_count = len(answer.split())
    length_score = min(word_count * 2, 20)

    # Sentiment score
    polarity = TextBlob(answer).sentiment.polarity

    if polarity > 0:
        sentiment_score = 20
    else:
        sentiment_score = 10

    # Filler words
    fillers = ["um", "uh", "like", "you know"]

    filler_penalty = sum(
        1 for filler in fillers
        if filler in answer_lower
    ) * 2

    # Final score
    total = (
        keyword_score
        + length_score
        + sentiment_score
        - filler_penalty
    )

    total = max(0, min(total, 100))

    return total


# =========================================================
# FACE DETECTION
# =========================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def detect_face(img_data):

    try:

        img_bytes = base64.b64decode(
            img_data.split(",")[1]
        )

        np_arr = np.frombuffer(
            img_bytes,
            np.uint8
        )

        frame = cv2.imdecode(
            np_arr,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            return 0

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_cascade.detectMultiScale(
            gray,
            1.3,
            5
        )

        return len(faces)

    except Exception:
        return 0


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/get_questions", methods=["POST"])
def get_questions():

    data = request.get_json()

    role = data.get("role")

    if role not in questions:
        return jsonify({
            "error": "Invalid role"
        }), 400

    selected_questions = random.sample(
        questions[role],
        5
    )

    return jsonify(selected_questions)


@app.route("/analyze", methods=["POST"])
def analyze():

    try:

        data = request.get_json()

        answer = data.get("answer", "")
        keywords = data.get("keywords", [])

        if not answer.strip():
            return jsonify({
                "error": "Answer cannot be empty"
            }), 400

        score = analyze_answer(
            answer,
            keywords
        )

        return jsonify({
            "score": score
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/face_check", methods=["POST"])
def face_check():

    try:

        data = request.get_json()

        image = data.get("image")

        faces = detect_face(image)

        return jsonify({
            "faces": faces
        })

    except Exception:

        return jsonify({
            "faces": 0
        })


# =========================================================
# FRONTEND
# =========================================================

PAGE = """

<!DOCTYPE html>

<html>

<head>

<title>AI Interviewer</title>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<style>

* {
    box-sizing: border-box;
}

body {

    margin: 0;

    font-family: 'Segoe UI', sans-serif;

    background:
    linear-gradient(
        135deg,
        #FAFAFA,
        #EAE4F2
    );

    color: #444444;
}


/* NAVBAR */

.navbar {

    background: white;

    padding: 15px 40px;

    box-shadow:
    0 2px 8px rgba(0,0,0,0.05);

    display: flex;

    justify-content: space-between;

    align-items: center;
}

.logo {

    font-weight: bold;

    font-size: 18px;
}

.nav-btn {

    background: #E4F2EC;

    padding: 8px 16px;

    border-radius: 20px;

    border: none;

    cursor: pointer;
}


/* HERO */

.hero {

    text-align: center;

    padding: 40px 20px 20px;
}

.hero h1 {

    font-size: 36px;

    margin-bottom: 10px;
}

.hero p {

    font-size: 16px;

    opacity: 0.7;
}


/* LOGIN */

#login {

    text-align: center;

    background: white;

    width: 500px;

    max-width: 90%;

    margin: 20px auto;

    padding: 30px;

    border-radius: 16px;

    box-shadow:
    0 8px 20px rgba(0,0,0,0.08);
}

#login h2 {

    margin-top: 0;
}

#role {

    padding: 12px;

    width: 220px;

    border: 1px solid #ddd;

    border-radius: 8px;

    font-size: 15px;
}


/* INTERVIEW */

#interview {

    width: 900px;

    max-width: 95%;

    margin: 30px auto;
}

.interview-card {

    width: 100%;

    background: white;

    border-radius: 16px;

    box-shadow:
    0 8px 20px rgba(0,0,0,0.08);

    display: flex;

    overflow: hidden;
}


/* CAMERA */

.left-panel {

    width: 40%;

    background: #E4F2EC;

    padding: 20px;

    text-align: center;
}

.left-panel h3 {

    margin-top: 0;
}

video {

    width: 100%;

    border-radius: 12px;

    background: #222;
}


/* QUESTION */

.right-panel {

    width: 60%;

    padding: 30px;
}

.question-box {

    background: #EAE4F2;

    padding: 15px;

    border-radius: 10px;

    margin-bottom: 15px;

    font-weight: bold;

    min-height: 50px;
}

textarea {

    width: 100%;

    height: 120px;

    border-radius: 10px;

    border: 2px solid #E4F2EC;

    padding: 12px;

    font-size: 15px;

    resize: vertical;
}

button {

    margin-top: 15px;

    background: #E4F2EC;

    border: none;

    padding: 11px 20px;

    border-radius: 8px;

    cursor: pointer;

    font-size: 14px;
}

button:hover {

    background: #F2E4E4;
}

#timer {

    margin-top: 15px;

    font-weight: bold;

    font-size: 16px;
}


/* RESULT */

#result {

    width: 800px;

    max-width: 90%;

    margin: 30px auto;

    padding: 30px;

    background: white;

    border-radius: 16px;

    box-shadow:
    0 8px 20px rgba(0,0,0,0.08);
}

#feedback {

    font-size: 18px;

    font-weight: bold;

    text-align: center;
}


/* RESPONSIVE */

@media (max-width: 700px) {

    .interview-card {

        flex-direction: column;
    }

    .left-panel,
    .right-panel {

        width: 100%;
    }

    .hero h1 {

        font-size: 28px;
    }
}

</style>

</head>


<body>


<!-- NAVBAR -->

<div class="navbar">

    <div class="logo">
        AI Interviewer
    </div>

    <button class="nav-btn">
        Live Demo
    </button>

</div>


<!-- HERO -->

<div class="hero">

    <h1>
        AI Virtual Interview Platform
    </h1>

    <p>
        Smart evaluation. Real-time analysis. Professional feedback.
    </p>

</div>


<!-- START INTERVIEW -->

<div id="login">

    <h2>
        Start Your Interview
    </h2>

    <p>
        Select your interview category
    </p>

    <select id="role">

        <option value="developer">
            Developer
        </option>

        <option value="hr">
            HR
        </option>

        <option value="general">
            General
        </option>

    </select>

    <br>

    <button onclick="start()">
        Start Interview
    </button>

</div>


<!-- INTERVIEW -->

<div id="interview" style="display:none;">

    <div class="interview-card">


        <!-- CAMERA -->

        <div class="left-panel">

            <h3>
                AI Monitoring Camera
            </h3>

            <video
                id="camera"
                autoplay
                muted
            ></video>

            <p id="cameraStatus">
                Camera starting...
            </p>

        </div>


        <!-- QUESTION + ANSWER -->

        <div class="right-panel">

            <div
                class="question-box"
                id="question"
            >
                Question appears here
            </div>


            <textarea
                id="answer"
                placeholder="Type your answer here..."
            ></textarea>


            <br>


            <button onclick="startSpeech()">
                🎙 Start Speaking
            </button>


            <button onclick="submitAnswer()">
                Submit
            </button>


            <div id="timer">
                Time: 30
            </div>

        </div>

    </div>

</div>


<!-- RESULT -->

<div
    id="result"
    style="display:none;"
>

    <h2>
        Interview Result
    </h2>

    <canvas id="chart"></canvas>

    <p id="feedback"></p>

    <div style="text-align:center;">

        <button onclick="location.reload()">
            Start New Interview
        </button>

    </div>

</div>


<script>


// =========================================================
// VARIABLES
// =========================================================

let questions = [];

let index = 0;

let scores = [];

let violations = 0;

let timer = 30;

let countdown = null;

let submitting = false;


// =========================================================
// TAB SWITCH DETECTION
// =========================================================

document.addEventListener(
    "visibilitychange",
    function() {

        if (document.hidden) {

            violations++;

            alert(
                "Tab switch detected!"
            );
        }

    }
);


// =========================================================
// START INTERVIEW
// =========================================================

async function start() {

    try {

        let role =
            document.getElementById(
                "role"
            ).value;


        let res = await fetch(
            "/get_questions",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                    "application/json"
                },

                body: JSON.stringify({
                    role: role
                })
            }
        );


        if (!res.ok) {

            throw new Error(
                "Could not load questions"
            );
        }


        questions =
            await res.json();


        if (
            !questions ||
            questions.length === 0
        ) {

            alert(
                "No questions found!"
            );

            return;
        }


        index = 0;

        scores = [];

        violations = 0;


        document.getElementById(
            "login"
        ).style.display = "none";


        document.getElementById(
            "interview"
        ).style.display = "block";


        askQuestion();

    }

    catch (error) {

        console.error(error);

        alert(
            "Error loading questions. Please try again."
        );
    }
}


// =========================================================
// SPEAK QUESTION
// =========================================================

function speak(text) {

    if (
        "speechSynthesis" in window
    ) {

        let msg =
            new SpeechSynthesisUtterance(
                text
            );

        speechSynthesis.speak(msg);
    }
}


// =========================================================
// ASK QUESTION
// =========================================================

function askQuestion() {


    clearInterval(countdown);


    if (
        index >= questions.length
    ) {

        finish();

        return;
    }


    let currentQuestion =
        questions[index];


    document.getElementById(
        "question"
    ).innerText =
        "Question " +
        (index + 1) +
        " of " +
        questions.length +
        ": " +
        currentQuestion.q;


    document.getElementById(
        "answer"
    ).value = "";


    speak(
        currentQuestion.q
    );


    timer = 30;


    document.getElementById(
        "timer"
    ).innerText =
        "Time: " + timer;


    countdown = setInterval(
        function() {

            timer--;


            document.getElementById(
                "timer"
            ).innerText =
                "Time: " + timer;


            if (timer <= 0) {

                clearInterval(
                    countdown
                );

                submitAnswer(
                    true
                );
            }

        },
        1000
    );
}


// =========================================================
// SUBMIT ANSWER
// =========================================================

async function submitAnswer(
    fromTimer = false
) {


    if (submitting) {
        return;
    }


    if (
        !questions ||
        questions.length === 0
    ) {

        alert(
            "Please start the interview first!"
        );

        return;
    }


    if (
        index >= questions.length
    ) {

        return;
    }


    clearInterval(
        countdown
    );


    let answer =
        document.getElementById(
            "answer"
        ).value.trim();


    if (
        answer === "" &&
        !fromTimer
    ) {

        alert(
            "Please enter your answer before submitting."
        );

        return;
    }


    if (
        answer === "" &&
        fromTimer
    ) {

        answer = "No answer provided";
    }


    submitting = true;


    try {


        let currentQuestion =
            questions[index];


        let res = await fetch(
            "/analyze",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                    "application/json"
                },

                body: JSON.stringify({

                    answer: answer,

                    keywords:
                        currentQuestion.keywords

                })

            }
        );


        if (!res.ok) {

            throw new Error(
                "Answer analysis failed"
            );
        }


        let data =
            await res.json();


        if (
            data.error
        ) {

            throw new Error(
                data.error
            );
        }


        scores.push(
            Number(data.score)
        );


        if (!fromTimer) {

            alert(
                "Answer submitted! Score: " +
                data.score
            );
        }


        index++;


        submitting = false;


        askQuestion();

    }

    catch (error) {

        submitting = false;

        console.error(error);

        alert(
            "Could not submit the answer. Please try again."
        );
    }
}


// =========================================================
// FINISH INTERVIEW
// =========================================================

function finish() {


    clearInterval(
        countdown
    );


    document.getElementById(
        "interview"
    ).style.display = "none";


    document.getElementById(
        "result"
    ).style.display = "block";


    let average = 0;


    if (
        scores.length > 0
    ) {

        average =
            scores.reduce(
                function(a, b) {
                    return a + b;
                },
                0
            ) / scores.length;
    }


    let integrity =
        Math.max(
            0,
            100 -
            (violations * 10)
        );


    new Chart(
        document.getElementById(
            "chart"
        ),
        {

            type: "bar",

            data: {

                labels: [
                    "Performance",
                    "Integrity"
                ],

                datasets: [

                    {
                        label:
                            "Score",

                        data: [
                            average,
                            integrity
                        ]
                    }

                ]
            },

            options: {

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100

                    }

                }

            }

        }
    );


    let feedback = "";


    if (average >= 70) {

        feedback =
            "Strong performance! Your answers were confident and relevant.";

    }

    else if (average >= 40) {

        feedback =
            "Average performance. Try to improve your clarity and include more relevant points.";

    }

    else {

        feedback =
            "Needs improvement. Practice answering interview questions with more detail.";
    }


    document.getElementById(
        "feedback"
    ).innerText =
        feedback +
        " Performance Score: " +
        average.toFixed(1) +
        "/100. Integrity Score: " +
        integrity +
        "/100.";
}


// =========================================================
// CAMERA + MICROPHONE
// =========================================================

navigator.mediaDevices
    .getUserMedia({
        video: true,
        audio: true
    })

    .then(
        function(stream) {

            document.getElementById(
                "camera"
            ).srcObject = stream;


            document.getElementById(
                "cameraStatus"
            ).innerText =
                "Camera and microphone ready.";

        }
    )

    .catch(
        function(error) {

            console.log(
                "Camera/Mic permission error:",
                error
            );


            document.getElementById(
                "cameraStatus"
            ).innerText =
                "Camera permission required.";
        }
    );


// =========================================================
// SPEECH RECOGNITION
// =========================================================

function startSpeech() {


    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;


    if (!SpeechRecognition) {

        alert(
            "Speech Recognition is not supported. Please use Google Chrome."
        );

        return;
    }


    const recognition =
        new SpeechRecognition();


    recognition.lang =
        "en-US";


    recognition.interimResults =
        false;


    recognition.continuous =
        false;


    recognition.onstart =
        function() {

            document.getElementById(
                "timer"
            ).innerText =
                "Listening...";
        };


    recognition.onresult =
        function(event) {


            const transcript =
                event.results[0][0]
                    .transcript;


            document.getElementById(
                "answer"
            ).value =
                transcript;


            document.getElementById(
                "timer"
            ).innerText =
                "Answer captured. Click Submit.";
        };


    recognition.onerror =
        function(event) {

            alert(
                "Microphone error: " +
                event.error
            );
        };


    recognition.onend =
        function() {

            if (
                index < questions.length
            ) {

                document.getElementById(
                    "timer"
                ).innerText =
                    "Time: " + timer;
            }
        };


    recognition.start();
}

</script>


</body>

</html>

"""


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )