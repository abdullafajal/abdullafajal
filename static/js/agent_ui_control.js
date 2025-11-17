// portfolio/static/js/agent_ui_control.js

document.addEventListener('DOMContentLoaded', function() {
    const chatOutput = document.getElementById('chat-output'); // Assuming chat output is here

    // Function to handle AI actions
    function handleAgentAction(actionType, actionValue) {
        if (!actionType) {
            console.log("No action type provided by agent.");
            return;
        }

        switch (actionType) {
            case 'navigate':
                console.log(`Navigating to: ${actionValue}`);
                window.location.href = actionValue;
                break;
            case 'highlight':
                console.log(`Highlighting element: ${actionValue}`);
                const elementToHighlight = document.querySelector(actionValue);
                if (elementToHighlight) {
                    elementToHighlight.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    // Optional: Add a temporary visual highlight
                    elementToHighlight.classList.add('temporary-highlight');
                    setTimeout(() => {
                        elementToHighlight.classList.remove('temporary-highlight');
                    }, 3000); // Remove highlight after 3 seconds
                } else {
                    console.warn(`Element with selector "${actionValue}" not found for highlighting.`);
                }
                break;
            case 'email':
                console.log(`Opening email client for: ${actionValue}`);
                window.location.href = `mailto:${actionValue}`;
                break;
            // Add more action types as needed
            default:
                console.warn(`Unknown action type: ${actionType}`);
        }
    }

    // This function would be called by your chat UI when a new agent response is received
    window.processAgentResponse = function(responseJson) {
        if (responseJson && responseJson.action) {
            handleAgentAction(responseJson.action.type, responseJson.action.value);
        }
    };

    // Add CSS for the temporary highlight
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes pulse-border {
            0% {
                border-color: var(--px-theme);
                box-shadow: 0 0 5px var(--px-theme);
            }
            50% {
                border-color: var(--px-theme-text);
                box-shadow: 0 0 20px var(--px-theme);
            }
            100% {
                border-color: var(--px-theme);
                box-shadow: 0 0 5px var(--px-theme);
            }
        }

        .temporary-highlight {
            border: 2px solid var(--px-theme);
            border-radius: 12px;
            animation: pulse-border 1.5s ease-in-out 2; /* Pulse twice */
        }
    `;
    document.head.appendChild(style);
});
