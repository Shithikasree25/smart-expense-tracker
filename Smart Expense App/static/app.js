function login(){
 fetch("/login",{method:"POST",headers:{'Content-Type':'application/json'},
 body:JSON.stringify({
  username:username.value,
  password:password.value
 })})
 .then(r=>r.json())
 .then(d=> d.success ? location="/dashboard" : alert(d.msg));
}

function register(){
 fetch("/register",{method:"POST",headers:{'Content-Type':'application/json'},
 body:JSON.stringify({
  username:username.value,
  password:password.value
 })})
 .then(r=>r.json()).then(d=>alert(d.msg));
}

function show(type){
 if(type==="add"){
  content.innerHTML=`<input id=t placeholder=Title>
  <input id=a type=number placeholder=Amount>
  <input id=c placeholder=Category>
  <button onclick=save()>Save</button>`;
 }
 if(type==="view"){
  fetch("/expenses").then(r=>r.json()).then(d=>{
   content.innerHTML=d.map(e=>`${e[0]} ₹${e[1]} (${e[2]})`).join("<br>");
  });
 }
}

function save(){
 fetch("/add_expense",{method:"POST",headers:{'Content-Type':'application/json'},
 body:JSON.stringify({
  title:t.value,amount:a.value,category:c.value
 })}).then(()=>{alert("Expense Added"); t.value=a.value=c.value="";});
}

function getAITip(){
 fetch("/ai_tip").then(r=>r.json()).then(d=>alert(d));
}
