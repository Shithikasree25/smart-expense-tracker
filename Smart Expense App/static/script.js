// ---------------- Show dynamic forms ----------------
function showForm(type){
    const formDiv = document.getElementById("dynamic-form");
    if(type === 'add'){
        formDiv.innerHTML = `
            <h3>Add Expense</h3>
            <input type="number" id="amount" placeholder="Amount">
            <input type="text" id="category" placeholder="Category">
            <button onclick="addExpense()">Add</button>
        `;
    } else {
        formDiv.innerHTML = '';
    }
}

// ---------------- Add expense ----------------
function addExpense(){
    const amount = document.getElementById("amount").value;
    const category = document.getElementById("category").value;

    if(!amount || !category){
        showPopup("Please fill all fields!");
        return;
    }

    fetch("/add_expense", {
        method: "POST",
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `amount=${amount}&category=${category}`
    }).then(res => res.json())
    .then(data => {
        showPopup(data.message); // default popup
        document.getElementById("amount").value = '';
        document.getElementById("category").value = '';
    });
}

// ---------------- Fetch all expenses ----------------
function fetchExpenses(){
    fetch("/get_expenses")
    .then(res => res.json())
    .then(data => {
        const list = data.map(e => `<p>${e.date}: ${e.category} - ₹${e.amount}</p>`).join('');
        document.getElementById("expense-list").innerHTML = list;
        showPopup("Expenses loaded!"); // default popup
    });
}

// ---------------- Fetch total expense ----------------
function fetchTotal() {
    fetch("/get_total")
    .then(res => res.json())
    .then(data => {
        showPopup("Total Expense: ₹" + data.total, "#4CAF50"); // green popup for total
    });
}

// ---------------- AI Tips ----------------
function aiTips() {
    fetch("/ai_tips")
    .then(res => res.json())
    .then(data => {
        showPopup(data.tip, "#4CAF50"); // green popup for AI tips
    });
}

// ---------------- Show/Hide chat box ----------------
function chatBox(){
    let chatDiv = document.getElementById("chat-box");
    if(!chatDiv){
        // Create chat container dynamically
        chatDiv = document.createElement("div");
        chatDiv.id = "chat-box";
        chatDiv.style.position = "fixed";
        chatDiv.style.bottom = "20px";
        chatDiv.style.right = "20px";
        chatDiv.style.width = "300px";
        chatDiv.style.height = "400px";
        chatDiv.style.background = "#f1f1f1";
        chatDiv.style.border = "1px solid #ccc";
        chatDiv.style.borderRadius = "8px";
        chatDiv.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
        chatDiv.style.display = "flex";
        chatDiv.style.flexDirection = "column";
        chatDiv.style.zIndex = "9999";
        chatDiv.style.overflow = "hidden";
        
        chatDiv.innerHTML = `
            <div id="chat-messages" style="flex:1; padding:10px; overflow-y:auto;"></div>
            <div style="display:flex; border-top:1px solid #ccc;">
                <input id="chat-input" type="text" placeholder="Type a message..." style="flex:1; padding:5px; border:none; outline:none;">
                <button onclick="sendChat()" style="padding:5px 10px; border:none; background:#4CAF50; color:white; cursor:pointer;">Send</button>
            </div>
        `;
        document.body.appendChild(chatDiv);
    } else {
        chatDiv.style.display = chatDiv.style.display === "none" ? "flex" : "none";
    }
}

// ---------------- Send chat message ----------------
function sendChat(){
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if(!message) return;

    const chatMessages = document.getElementById("chat-messages");
    chatMessages.innerHTML += `<p><b>You:</b> ${message}</p>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: message})
    })
    .then(res => res.json())
    .then(data => {
        chatMessages.innerHTML += `<p><b>AI:</b> ${data.response}</p>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    })
    .catch(() => {
        chatMessages.innerHTML += `<p><b>AI:</b> AI service unavailable.</p>`;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    input.value = '';
}

// ---------------- Generic popup function ----------------
function showPopup(message, color = "#333") {
    const popup = document.createElement("div");
    popup.className = "alert";
    popup.innerText = message;
    document.body.appendChild(popup);

    // Style popup
    popup.style.display = "block";
    popup.style.position = "fixed";
    popup.style.top = "20px"; // float from top
    popup.style.right = "20px"; // float on right side
    popup.style.background = color; // dynamic color
    popup.style.color = "#fff";
    popup.style.padding = "10px 20px";
    popup.style.borderRadius = "5px";
    popup.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
    popup.style.zIndex = "9999";
    popup.style.fontWeight = "bold";

    // Auto remove after 3 seconds
    setTimeout(() => {
        popup.remove();
    }, 3000);
}
