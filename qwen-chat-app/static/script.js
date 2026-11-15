const form = document.getElementById("chat-form");
const input = document.getElementById("prompt");
const sendButton = document.getElementById("send");
const messagesEl = document.getElementById("messages");
const welcome = document.getElementById("welcome");
const newChatButton = document.getElementById("new-chat");

let history = [
  { role: "system", content: "You are a helpful, clear, and accurate AI assistant. For code questions, provide practical explanations and working examples." }
];

function addMessage(role, content, extraClass = "") {
  welcome.hidden = true;
  const row = document.createElement("div");
  row.className = `message ${role} ${extraClass}`.trim();

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = role === "user" ? "You" : "Q";

  const body = document.createElement("div");
  body.className = "message-content";
  body.textContent = content;

  row.append(avatar, body);
  messagesEl.appendChild(row);
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
  return row;
}

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean || sendButton.disabled) return;

  addMessage("user", clean);
  history.push({ role: "user", content: clean });
  input.value = "";
  input.style.height = "auto";
  sendButton.disabled = true;

  const pending = addMessage("assistant", "Qwen is thinking…", "typing");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: history })
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);

    pending.classList.remove("typing");
    pending.querySelector(".message-content").textContent = data.reply;
    history.push({ role: "assistant", content: data.reply });
  } catch (error) {
    pending.querySelector(".message-content").textContent = `Error: ${error.message}`;
    pending.classList.remove("typing");
    // Remove the unanswered user turn so the user can retry cleanly.
    history.pop();
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
});

input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

newChatButton.addEventListener("click", () => {
  history = [history[0]];
  messagesEl.replaceChildren();
  welcome.hidden = false;
  input.focus();
});

document.querySelectorAll(".suggestion").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});
