from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# ================= QUESTIONS ================= #

questions = {
"developer":[
{"q":"Explain hash table and collision handling.","keywords":["hash","collision","probing","chaining"]},
{"q":"Process vs Thread difference.","keywords":["process","thread","memory"]},
{"q":"Explain quicksort worst case.","keywords":["pivot","partition","n^2"]},
{"q":"Database normalization 1NF 2NF 3NF.","keywords":["normal","redundancy"]},
{"q":"REST vs GraphQL.","keywords":["rest","graphql"]},
{"q":"What is deadlock?","keywords":["deadlock","resource"]},
{"q":"Explain memory management in OS.","keywords":["paging","memory"]},
{"q":"Database indexing and B-tree.","keywords":["index","btree"]},
{"q":"TCP vs UDP.","keywords":["tcp","udp"]},
{"q":"Recursion vs iteration.","keywords":["recursion","stack"]},
{"q":"Explain CAP theorem.","keywords":["cap","consistency"]},
{"q":"Race condition in multithreading.","keywords":["race","thread"]},
{"q":"Garbage collection.","keywords":["memory","cleanup"]},
{"q":"MVC architecture.","keywords":["model","view"]},
{"q":"How compiler works.","keywords":["lexer","parser"]}
],

"hr":[
{"q":"Tell me about a failure.","keywords":["learn","failure"]},
{"q":"Lead a team under pressure.","keywords":["team","lead"]},
{"q":"Why should we hire you?","keywords":["skills","fit"]},
{"q":"Conflict resolution example.","keywords":["conflict","resolve"]},
{"q":"Biggest achievement.","keywords":["achievement"]},
{"q":"Handle tight deadlines.","keywords":["deadline"]},
{"q":"Initiative example.","keywords":["initiative"]},
{"q":"What motivates you?","keywords":["motivation"]},
{"q":"Adapt to new environment.","keywords":["adapt"]},
{"q":"Where in 5 years?","keywords":["future"]},
{"q":"Solve difficult problem.","keywords":["problem"]},
{"q":"Strengths and weaknesses.","keywords":["strength"]},
{"q":"Handle criticism.","keywords":["feedback"]},
{"q":"Prioritize tasks.","keywords":["priority"]},
{"q":"Why this career?","keywords":["passion"]}
],

"general":[
{"q":"What is leadership?","keywords":["lead"]},
{"q":"What is success?","keywords":["goal"]},
{"q":"Manage stress.","keywords":["stress"]},
{"q":"What is teamwork?","keywords":["team"]},
{"q":"Decision making process.","keywords":["decision"]},
{"q":"How stay productive?","keywords":["focus"]},
{"q":"Critical thinking.","keywords":["logic"]},
{"q":"Time management.","keywords":["time"]},
{"q":"Great employee traits.","keywords":["discipline"]},
{"q":"Handle pressure.","keywords":["pressure"]},
{"q":"Adaptability.","keywords":["adapt"]},
{"q":"Problem solving.","keywords":["solution"]},
{"q":"Self improvement.","keywords":["learn"]},
{"q":"Innovation.","keywords":["idea"]},
{"q":"Responsibility.","keywords":["responsible"]}
]
}

# ================= MEMORY ================= #

completed_interviews = 0
last_score = 0

# ================= UI ================= #

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>VIRTUAL HR</title>
<style>
body{
font-family:Segoe UI;
background:#FAFAFA;
color:#444;
text-align:center;
margin:0;
}
.nav{
background:#EAE4F2;
padding:15px;
font-weight:bold;
}
.card{
background:white;
padding:20px;
margin:20px auto;
width:60%;
border-radius:12px;
box-shadow:0 4px 10px rgba(0,0,0,0.05);
}
button{
padding:10px 20px;
border:none;
border-radius:8px;
background:#E4F2EC;
cursor:pointer;
margin:5px;
}
button:hover{background:#F2E4E4;}
textarea{
width:80%;
height:100px;
border-radius:8px;
border:1px solid #ccc;
padding:10px;
}
</style>
</head>
<body>

<div class="nav">VIRTUAL HR</div>

<div class="card">
<h2>AI Interview Platform</h2>
<select id="role">
<option value="developer">Developer</option>
<option value="hr">HR</option>
<option value="general">General</option>
</select>
<br><br>
<button onclick="start()">Start Interview</button>
</div>

<div class="card" id="interview" style="display:none">
<h3 id="question"></h3>
<textarea id="answer" placeholder="Type your answer..."></textarea><br>
<button onclick="submitAnswer()">Submit</button>
</div>

<div class="card">
<h3>Stats</h3>
<p>Completed Interviews: <span id="count">0</span></p>
<p>Last Score: <span id="score">0</span></p>
</div>

<script>

function start(){
let role=document.getElementById("role").value;
fetch("/get?role="+role).then(r=>r.json()).then(d=>{
document.getElementById("question").innerText=d.q;
document.getElementById("interview").style.display="block";
});
}

function submitAnswer(){
let ans=document.getElementById("answer").value;
fetch("/analyze",{method:"POST",headers:{"Content-Type":"application/json"},
body:JSON.stringify({answer:ans})})
.then(r=>r.json()).then(d=>{
alert("Score: "+d.score);
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
    return PAGE

@app.route("/get")
def get_q():
    role=request.args.get("role","developer")
    q=random.choice(questions[role])
    return jsonify(q)

@app.route("/analyze",methods=["POST"])
def analyze():
    global completed_interviews,last_score
    data=request.json
    ans=data["answer"].lower()

    score=min(len(ans.split())*3,100)

    completed_interviews+=1
    last_score=score

    return jsonify({"score":score})

@app.route("/stats")
def stats():
    return jsonify({"count":completed_interviews,"score":last_score})

# ================= RUN ================= #

if __name__=="__main__":
    app.run(debug=True)
