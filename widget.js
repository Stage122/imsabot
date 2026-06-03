<!-- Inserisci questo snippet prima di </body> nel sito imsasrl.it -->
<script>
(function(){
const API_BASE = "https://TUO_BACKEND_DOMAIN:8000"; // sostituisci con l'URL del backend (http://localhost:8000 per test)
const API = API_BASE + "/chat";
const HANDOFF = API_BASE + "/handoff";
const SESSION_API = API_BASE + "/session";
const sessionId = "sess_" + Math.random().toString(36).slice(2,9);

// widget container
const container = document.createElement("div");
container.id = "imsa-chat-widget";
container.style = "position:fixed;bottom:20px;right:20px;width:360px;max-height:520px;background:white;border:1px solid #ccc;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.1);overflow:hidden;font-family:Arial,z-index:99999;";
container.innerHTML = `

<div style="background:#0A66C2;color:white;padding:10px;display:flex;justify-content:space-between;align-items:center;">
  <div><strong>Chat IMSA</strong></div>
  <div style="font-size:12px;">Italiano • Consigli</div>
</div>
<div id="imsa-messages" style="padding:10px;height:340px;overflow:auto;background:#fafafa;"></div>
<div style="padding:10px;border-top:1px solid #eee;">
  <input id="imsa-input" style="width:100%;box-sizing:border-box;padding:8px" placeholder="Scrivi la tua domanda..."/>
  <div style="margin-top:8px;display:flex;gap:8px;">
    <button id="imsa-send">Invia</button>
    <button id="imsa-handoff">Parla con un operatore</button>
  </div>
</div>
`;
document.body.appendChild(container);

const messagesEl = document.getElementById("imsa-messages");
const inputEl = document.getElementById("imsa-input");
document.getElementById("imsa-send").onclick = async () => {

const msg = inputEl.value.trim();
if(!msg) return;
appendMessage("Tu", msg);
inputEl.value = "";
try {
  const res = await fetch(API, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({session_id: sessionId, message: msg})
  });
  const data = await res.json();
  appendMessage("IMSA", data.answer || "Errore nella risposta");
} catch (e) {
  appendMessage("Sistema", "Errore di connessione al server.");
}
};

document.getElementById("imsa-handoff").onclick = async () => {

const msg = inputEl.value.trim() || "Richiedo contatto operatore";
try {
  await fetch(HANDOFF, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({session_id: sessionId, message: msg})
  });
  appendMessage("Sistema", "Richiesta inoltrata all'operatore. Verrai contattato a breve.");
} catch (e) {
  appendMessage("Sistema", "Errore nell'inoltro al'operatore.");
}
};

function appendMessage(who, text){

const el = document.createElement("div");
el.style.marginBottom = "8px";
el.innerHTML = "<strong>"+who+"</strong>: "+text;
messagesEl.appendChild(el);
messagesEl.scrollTop = messagesEl.scrollHeight;
}

// Poll session messages (to receive operator replies)
async function pollSession(){

try {
  const res = await fetch(SESSION_API + "/" + sessionId);
  const data = await res.json();
  if(data && data.messages){
    // clear and re-render
    messagesEl.innerHTML = "";
    data.messages.forEach(m => {
      const who = m.from === "user" ? "Tu" : (m.from === "bot" ? "IMSA" : (m.from === "operator" ? "Operatore" : m.from));
      appendMessage(who, m.text);
    });
  }
} catch(e){
  // ignore polling errors
} finally {
  setTimeout(pollSession, 3000);
}
}
pollSession();

})();
</script>
