from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# ================= QUESTION BANK ================= #

questions = {
"developer":[
{"q":"Explain hash table collision handling.","k":["hash","collision"]},
{"q":"Explain quicksort worst case.","k":["pivot","n2"]},
{"q":"Explain CAP theorem.","k":["consistency","availability"]},
{"q":"Process vs Thread.","k":["process","thread"]},
{"q":"Explain race condition.","k":["race"]},
{"q":"Explain REST.","k":["http","stateless"]},
{"q":"What is deadlock?","k":["deadlock"]},
{"q":"Explain memory management.","k":["memory"]},
{"q":"Compiler working?","k":["parser"]},
{"q":"Database indexing?","k":["index"]},
{"q":"Explain recursion stack.","k":["stack"]},
{"q":"TCP vs UDP.","k":["tcp","udp"]},
{"q":"Garbage collection?","k":["memory"]},
{"q":"Explain MVC.","k":["model"]},
{"q":"Normalization?","k":["normal"]}
],
"hr":[
{"q":"Tell me about a failure.","k":["learn"]},
{"q":"Leadership example.","k":["team"]},
{"q":"Conflict resolution.","k":["resolve"]},
{"q":"Why hire you?","k":["skills"]},
{"q":"Biggest achievement.","k":["achievement"]},
{"q":"Handle criticism.","k":["feedback"]},
{"q":"Deadline pressure.","k":["deadline"]},
{"q":"Weakness?","k":["weakness"]},
{"q":"Future goals.","k":["future"]},
{"q":"Initiative example.","k":["initiative"]},
{"q":"Solve tough problem.","k":["problem"]},
{"q":"Adapt to change.","k":["adapt"]},
{"q":"Motivation?","k":["motivation"]},
{"q":"Prioritize tasks.","k":["priority"]},
{"q":"Why this career?","k":["career"]}
],
"general":[
{"q":"Define leadership.","k":["lead"]},
{"q":"What is success?","k":["goal"]},
{"q":"Manage stress.","k":["stress"]},
{"q":"Critical thinking.","k":["logic"]},
{"q":"Problem solving.","k":["solution"]},
{"q":"Time management.","k":["time"]},
{"q":"Teamwork.","k":["team"]},
{"q":"Innovation example.","k":["idea"]},
{"q":"Adaptability.","k":["adapt"]},
{"q":"Decision making.","k":["decision"]},
{"q":"Responsibility.","k":["responsible"]},
{"q":"Self improvement.","k":["learn"]},
{"q":"Handle pressure.","k":["pressure"]},
{"q":"Productivity tips.","k":["focus"]},
{"q":"Good employee traits.","k":["discipline"]}
]
}

# ================= UI ================= #

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>VIRTUAL HR</title>

<style>
body{
margin:0;
font-family:Segoe UI;
background:#FAFAFA;
color:#444;
}

/* TOP BAR */
.top{
background:#EAE4F2;
padding:18px;
font-weight:bold;
}

/* DASHBOARD */
.dashboard{
display:flex;
height:100vh;
}

/* SIDEBAR */
.sidebar{
width:220px;
background:#E4F2EC;
padding:20px;
}
.sidebar h3{margin-bottom:20px}
.sidebar button{
width:100%;
padding:10px;
margin:6px 0;
border:none;
border-radius:8px;
background:white;
cursor:pointer;
}

/* MAIN PANEL */
.main{
flex:1;
padding:30px;
}

/* GLASS CARDS */
.card{
background:white;
border-radius:14px;
padding:20px;
margin-bottom:20px;
box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

/* INTERVIEW MODE */
#interview{display:none;text-align:center}
video{
width:320px;
border-radius:12px;
border:3px solid #EAE4F2;
}
.bubble{
background:#EAE4F2;
padding:12px;
border-radius:12px;
margin:10px;
}
.answer{background:#F2E4E4}

.timer{
font-weight:bold;
color:#888;
}
</style>
</head>

<body>

<div class="top">VIRTUAL HR</div>

<div class="dashboard">

<!-- SIDEBAR -->
<div class="sidebar">
<h3>Menu</h3>
<button onclick="showHome()">Home</button>
<button onclick="startInterview()">Start Interview</button>
</div>

<!-- MAIN -->
<div class="main">

<div id="home">
<div class="card">
<h2>Welcome to VIRTUAL HR</h2>
<p>AI Interview • Integrity Monitoring • Smart Evaluation</p>

<select id="role">
<option value="developer">Developer</option>
<option value="hr">HR</option>
<option value="general">General</option>
</select>
</div>
</div>

<div id="interview">

<video id="camera" autoplay playsinline></video>

<div class="bubble" id="question"></div>
<div class="bubble answer" id="answer">Speak your answer...</div>

<div class="timer">Time left: <span id="time">20</span>s</div>

<button onclick="startSpeech()">🎤 Speak</button>
<button onclick="submitAnswer()">Submit</button>

</div>

</div>
</div>

<script>

let timer=20;
let countdown;
let violations=0;

// CAMERA
navigator.mediaDevices.getUserMedia({video:true,audio:true})
.then(s=>document.getElementById("camera").srcObject=s);

// TAB SWITCH
document.addEventListener("visibilitychange",()=>{
if(document.hidden) violations++;
});

function showHome(){
document.getElementById("home").style.display="block";
document.getElementById("interview").style.display="none";
}

// START INTERVIEW
function startInterview(){
document.getElementById("home").style.display="none";
document.getElementById("interview").style.display="block";

fetch("/get?role="+document.getElementById("role").value)
.then(r=>r.json())
.then(d=>{
document.getElementById("question").innerText=d.q;
startTimer();
});
}

// TIMER
function startTimer(){
timer=20;
document.getElementById("time").innerText=timer;

countdown=setInterval(()=>{
timer--;
document.getElementById("time").innerText=timer;

if(timer<=0){
clearInterval(countdown);
submitAnswer();
}
},1000);
}

// SPEECH
function startSpeech(){
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if(!SpeechRecognition){alert("Use Chrome");return;}

const rec=new SpeechRecognition();
rec.lang="en-US";

rec.onresult=e=>{
let text=e.results[0][0].transcript;
document.getElementById("answer").innerText=text;
window.answer=text;
};
rec.start();
}

// SUBMIT
function submitAnswer(){
clearInterval(countdown);

fetch("/analyze",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
answer:window.answer||"",
violations:violations
})
})
.then(r=>r.json())
.then(d=>{
alert(
"Performance: "+d.score+
"\\nIntegrity: "+d.integrity+
"\\nHire Probability: "+d.hire+"%"
);
location.reload();
});
}

</script>
</body>
</html>
"""

# ================= ROUTES ================= #

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/get")
def get_q():
    role=request.args.get("role","developer")
    return jsonify(random.choice(questions[role]))

@app.route("/analyze",methods=["POST"])
def analyze():
    data=request.json
    words=len(data["answer"].split())
    score=min(words*5,100)
    integrity=max(100-data["violations"]*15,0)
    hire=int(score*0.7+integrity*0.3)
    return jsonify({"score":score,"integrity":integrity,"hire":hire})

if __name__=="__main__":
    app.run(debug=True)
