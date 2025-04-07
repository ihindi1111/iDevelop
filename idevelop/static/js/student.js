"use strict";

let appendedFriends = new Set();
let appendedRequests = new Set();

function getFriendStream() {
    $.ajax({
        url: getListURL,
        dataType: "json",
        success: updateFriendStream,
        error: updateError
    });
}

function updateError(xhr) {
    if (xhr.status === 0) {
        displayError("Cannot connect to server");
        return;
    }

    if (!xhr.getResponseHeader("content-type").includes("application/json")) {
        displayError(`Received status=${xhr.status}`);
        return;
    }

    let response = JSON.parse(xhr.responseText);
    if (response.hasOwnProperty("error")) {
        displayError(response.error);
        return;
    }

    displayError(response);
}

function displayError(message) {
    $("#error").html(message);
}

function updateFriendStream(data) {
    // Update each section of the friend stream
    updateFriends(data.friends);
    updateIncomingRequests(data.incoming_requests);
    updateOutgoingRequests(data.outgoing_requests);
    updateRegularStudents(data.regular_students);
}

function updateFriends(friends) {
    $("#friends-list").empty();
    appendedFriends.clear(); // Reset the Set when the list is cleared
    friends.forEach(friend => appendFriendWithState(friend));
}

function appendFriendWithState(friend) {
    if (appendedFriends.has(friend.id) || document.getElementById(`friend-${friend.id}`)) {
        return; // Skip if already present
    }
    const friendHtml = makeFriendItem(friend);
    $("#friends-list").append(friendHtml);
    appendedFriends.add(friend.id); // Track appended friend
}

function makeFriendItem(friend) {
    return `
        <li class="student-item" id="friend-${friend.id}">
            <span class="student-name">${sanitize(friend.user__username)}</span>
            <button class="btn remove-friend" onclick="removeFriend('${friend.id}')">Remove</button>
        </li>`;
}

function updateIncomingRequests(requests) {
    const incomingList = $("#incoming-requests-list");
    const currentIds = new Set(
        incomingList.children().map((_, el) => $(el).attr("id").replace("incoming-request-", "")).get()
    );

    const newRequestIds = new Set(requests.map(request => request.id.toString()));

    // Remove stale requests
    currentIds.forEach(id => {
        if (!newRequestIds.has(id)) {
            $(`#incoming-request-${id}`).remove();
        }
    });

    // Add new requests
    requests.forEach(request => {
        if (!currentIds.has(request.id.toString())) {
            appendIncomingRequestWithState(request);
        }
    });
}


function appendIncomingRequestWithState(request) {
    if (appendedRequests.has(request.id)) {
        return;
    }

    const requestHtml = makeIncomingRequestItem(request);
    $("#incoming-requests-list").append(requestHtml);
    appendedRequests.add(request.id);
}

function makeIncomingRequestItem(request) {
    return `
        <li class="student-item" id="incoming-request-${request.id}">
            <span class="student-name">${sanitize(request.from_user__username)}</span>
            <button class="btn accept-request" onclick="acceptFriendRequest(${request.id})">Accept</button>
        </li>`;
}

function updateOutgoingRequests(requests) {
    $("#outgoing-requests-list").empty();
    requests.forEach(request => appendOutgoingRequestWithState(request));
}

function appendOutgoingRequestWithState(request) {
    const requestHtml = makeOutgoingRequestItem(request);
    $("#outgoing-requests-list").append(requestHtml);
}

function makeOutgoingRequestItem(request) {
    return `
        <li class="student-item" id="outgoing-request-${request.id}">
            <span class="student-name">${sanitize(request.to_user__username)}</span>
            <button class="btn cancel-request" onclick="cancelFriendRequest(${request.id})">Cancel</button>
        </li>`;
}

function updateRegularStudents(students) {
    $("#regular-students-list").empty();
    students.forEach(student => appendRegularStudentWithState(student));
}

function appendRegularStudentWithState(student) {
    const studentHtml = makeRegularStudentItem(student);
    $("#regular-students-list").append(studentHtml);
}

function makeRegularStudentItem(student) {
    return `
        <li class="student-item" id="student-${student.id}">
            <span class="student-name">${sanitize(student.username)}</span>
            <button class="btn add-friend" onclick="sendFriendRequest(${student.id})">Add</button>
        </li>`;
}

function sendFriendRequest(studentId) {
    $.ajax({
        url: sendFriendRequestURL.replace("0", studentId),
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType: "json",
        success: function (data) {
            removeFromRegularStudents(studentId);
            appendOutgoingRequestWithState(data.outgoing_request);
        },
        error: updateError
    });
}

function acceptFriendRequest(requestId) {
    $.ajax({
        url: acceptFriendRequestURL.replace("0", requestId),
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType: "json",
        success: function (data) {
            removeFromIncomingRequests(requestId);
            appendFriendWithState(data.friend);
        },
        error: updateError
    });
}

function cancelFriendRequest(requestId) {
    $.ajax({
        url: cancelFriendRequestURL.replace("0", requestId),
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType: "json",
        success: function (data) {
            removeFromOutgoingRequests(requestId);
        },
        error: updateError
    });
}

function removeFriend(id) {
    $.ajax({
        url: removeFriendURL.replace("0", id), // Replace "0" in the URL with the friend ID
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        dataType: "json",
        success: function (data) {
            removeFromFriendsList(id); // Pass the ID to the removeFromFriendsList function
        },
        error: updateError // Handle errors
    });
}

function removeFromIncomingRequests(requestId) {
    $(`#incoming-request-${requestId}`).remove();
}

function removeFromOutgoingRequests(requestId) {
    $(`#outgoing-request-${requestId}`).remove();
}

function removeFromRegularStudents(studentId) {
    $(`#student-${studentId}`).remove();
}

function removeFromFriendsList(iD) {
    $(`#friends-list li:contains('${iD}')`).remove();
}

function sanitize(s) {
    return s.replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "unknown";
}
