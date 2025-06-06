const firebaseConfig = {
    apiKey: "AIzaSyC57YV45aQ0VwWEKA26kswphT4J0RKpvgs",
    authDomain: "vidnik-pn.firebaseapp.com",
    projectId: "vidnik-pn",
    storageBucket: "vidnik-pn.appspot.com",
    messagingSenderId: "298821539958",
    appId: "1:298821539958:web:e186b5ae09878ee4592757",
    measurementId: "G-E4GPHBSNH5"
};

const app = firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();


// Handle incoming messages
messaging.onMessage((payload) => {
    // console.log('Message received. ', payload);
    console.log('Message received.');

    // Display notification manually when app is in foreground
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
    };

    if (Notification.permission === "granted") {
        const notification = new Notification(notificationTitle, notificationOptions);
    }
});
    

// Request permission to send notifications
document.getElementById('notifyButton').addEventListener('click', function() {
    // Check if the browser supports notifications
    if ('Notification' in window) {
        // Request notification permission
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                // If permission granted, get the FCM token
                getToken();
            } else {
                console.log('Notification permission denied.');
            }
        });
    } else {
        alert('Your browser does not support notifications.');
    }
});


// Send a demo notification
const demoNotifyButton = document.getElementById('demoNotifyButton');
if (demoNotifyButton) {
    // Send a demo notification
    demoNotifyButton.addEventListener('click', function() {
        messaging.getToken({ vapidKey: "BJFCIgh8Nk1DxUVNkIMRZg_h0L-ZPYvPBpjgdK2HZIPIe6-NV5tdsEHqRKhEErBw_5Sf6BS2Wm7kqACPHGeyTSE" })
            .then((token) => {
                if (token) {
                    fetch('/send-demo-notification/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({ token: token })
                    }).then(response => response.json())
                      .then(() => console.log("Demo notification sent."))
                      .catch(error => console.error('Error sending demo notification:', error));
                } else {
                    console.log('No registration token available.');
                }
            }).catch((err) => {
                console.error('Error retrieving token:', err);
            });
    });
} else {
    console.log("Button not found: demoNotifyButton");
}





function getToken() {
    messaging.getToken({ vapidKey: "BJFCIgh8Nk1DxUVNkIMRZg_h0L-ZPYvPBpjgdK2HZIPIe6-NV5tdsEHqRKhEErBw_5Sf6BS2Wm7kqACPHGeyTSE" })
        .then((currentToken) => {
            if (currentToken) {
                console.log(currentToken);
                sendTokenToServer(currentToken);
            } else {
                console.log('No registration token available. Request permission to generate one.');
            }
        }).catch((err) => {
            console.log('An error occurred while retrieving token. ', err);
            document.getElementById('token').textContent = 'click again';
        });
}

function sendTokenToServer(token) {
    fetch('/save-token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ token: token })
    }).then(response => response.json())
        // .then(data => console.log(data))
        .then(data => console.log("Notification token saved."))
        .catch(error => console.error('Error:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


