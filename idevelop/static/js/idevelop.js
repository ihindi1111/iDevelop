"use strict"

/*
 * Use a global variable for the socket.  Poor programming style, I know,
 * but I think the simpler implementations of the deleteItem() and addItem()
 * functions will be more approachable for students with less JS experience.
 */
let socket = null
let isTyping = false;
let typingTimeout;

document.addEventListener("DOMContentLoaded", () => {
    update_if_active();
    check_permissions();
    implement_tab_press();
    connectToServer(); // Ensure WebSocket connection initializes
});


function adjusting_sms_box(){
    const sidebar = document.getElementById("sidebar");
    const container = document.querySelector(".container");

    let isResizing = false;

    sidebar.addEventListener("mousedown", function (e) {
        if (Math.abs(e.clientX - sidebar.getBoundingClientRect().left) <= 20) {
            isResizing = true;
            document.body.style.cursor = "ew-resize"; 
        }
    });

    window.addEventListener("mousemove", function (e) {
        if (isResizing) {
            const newWidth = container.getBoundingClientRect().right - e.clientX;
            if (newWidth > 50 && newWidth < container.getBoundingClientRect().width) {
                sidebar.style.width = `${newWidth}px`;
                container.style.gridTemplateColumns = `${newWidth}px 1fr`;
            }
        }
    });


    window.addEventListener("mouseup", function () {
        isResizing = false;
        document.body.style.cursor = "default";
    });
}

function update_if_active(){
    document.getElementById("id_collab_box").addEventListener("input", () => {
        isTyping = true;
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            isTyping = false;
        }, 2000);
    });
}

function check_permissions(){
    const collabBox = document.getElementById("id_collab_box");
    const isReadOnly = collabBox.getAttribute("data-readonly") === "true";
    collabBox.readOnly = isReadOnly;
    if (isReadOnly){
        const messageBox = document.getElementById("message")
        messageBox.textContent = "You only have viewing permissions. Request permissions in your friends profile page"
    }
}

function implement_tab_press(){
    const collabBox = document.getElementById("id_collab_box");
    collabBox.addEventListener("keydown", (event) => {
        if (event.key === "Tab") {
            event.preventDefault();
            const start = collabBox.selectionStart;
            const end = collabBox.selectionEnd;
            collabBox.value = collabBox.value.substring(0, start) + "\t" + collabBox.value.substring(end);
            collabBox.selectionStart = collabBox.selectionEnd = start + 1;
        }
    });
}

function connectToServer() {
    // Use wss: protocol if site using https:, otherwise use ws: protocol
    let wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:"

    // Create a new WebSocket.
    let url = `${wsProtocol}//${window.location.host}/idevelop/collab`
    socket = new WebSocket(url)

    // Handle any errors that occur.
    socket.onerror = function(error) {
        displayMessage("WebSocket Error: " + error)
    }

    // Show a connected message when the WebSocket is opened.
    socket.onopen = function(event) {
        displayMessage("WebSocket Connected")
        setInterval(() => {
            if (isTyping) {
                update_text();
            }
        }, 1500);
        // setInterval(() => {get_collab_text();}, 8000);
    }

    // Show a disconnected message when the WebSocket is closed.
    socket.onclose = function(event) {
        displayMessage("WebSocket Disconnected")
    }

    // Handle messages received from the server.
    socket.onmessage = function(event) {
        let response = JSON.parse(event.data);

        if (response && response.type === 'update' && response.data) {
            updateCollab(response.data);
        } else if (response && response.type === "error" && response.data) {
            displayError(response.data);
        } else if (response && response.type === "message" && response.message) {
            displayMessage(response.data);
        } else {
            console.warn("Unexpected response format:", response);
        }

    }
}

function displayError(message) {
    let errorElement = document.getElementById('message')
    errorElement.textContent = message
}

function displayMessage(message) {
    let errorElement = document.getElementById("message")
    errorElement.value = message
}

function displayResponse(response) {
    if ("error" in response) {
        displayError(response.error)
    } else if ("message" in response) {
        displayMessage(response.message)
    } else {
        displayMessage("Unknown response")
    }
}

function updateCollab(response) {
    let new_text = response.text
    let text_area = document.getElementById("id_collab_box")
    if (response.id == collabBoxID){
        text_area.value = new_text}
    return 
}

function update_text() {
    let textInputEl = document.getElementById("id_collab_box")
    let itemText = textInputEl.value

    console.log("collabBoxID:", collabBoxID);  
    console.log("myUserID:", myUserID);
    console.log("ownerOfCollabBoxID:", ownercollabBoxID);
    displayError("")
    // In the future want to replace id with an actual dynamic id
    let data = {action: "update", text: itemText, id: myUserID, box_id: collabBoxID, owner_id: ownercollabBoxID}
    socket.send(JSON.stringify(data))
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}