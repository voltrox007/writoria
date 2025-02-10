document.addEventListener("DOMContentLoaded", () => {
    const chatButton = document.getElementById("chat-button");
    const chatInterface = document.getElementById("chat-interface");
    const closeChat = document.getElementById("close-chat");
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatMessages = document.getElementById("chat-messages");
    const signOutButton = document.getElementById("sign-out"); // Add reference to sign-out button

    function getPageContent() {
        return document.body.innerText.replace(/\s+/g, ' ').trim();
    }

    chatButton.addEventListener("click", () => {
        chatInterface.style.display = "flex";
        chatInterface.classList.add("fade-in");
        chatButton.style.display = "none";

        // Show welcome message only once per sign-in session
        if (!sessionStorage.getItem("welcomeMessageShown")) {
            setTimeout(() => {
                displayMessage("Rick", "Hey there! I'm Rick. Ask me anything about this page.", "bot-message");
                sessionStorage.setItem("welcomeMessageShown", "true");
            }, 500);
        }
    });

    closeChat.addEventListener("click", () => {
        chatInterface.classList.add("fade-out");
        setTimeout(() => {
            chatInterface.style.display = "none";
            chatInterface.classList.remove("fade-out");
            chatButton.style.display = "block";
        }, 500);
    });

    chatForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = userInput.value;
        userInput.value = "";

        if (message.trim() === "") return;

        // Display user message
        displayMessage("You", message, "user-message");

        // Typing Animation
        const typingIndicator = document.createElement("div");
        typingIndicator.className = "typing-indicator";
        typingIndicator.innerHTML = "<span>.</span><span>.</span><span>.</span>";
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Send question + page content
        fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 
                message: message, 
                page_content: getPageContent() 
            }),
        })
        .then((response) => response.json())
        .then((data) => {
            typingIndicator.remove();
            displayMessage("Rick", data.response, "bot-message");
        });
    });

    function displayMessage(sender, message, className) {
        const messageElement = document.createElement("div");
        messageElement.className = `message ${className}`;
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Sign-Out Event (Clears session storage)
    if (signOutButton) {
        signOutButton.addEventListener("click", () => {
            sessionStorage.removeItem("welcomeMessageShown"); // Reset welcome message flag
        });
    }
});
