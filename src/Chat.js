import React, { useState } from 'react';

function Chat({ onNewMessage }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim()) {
            const newMessages = [...messages, { text: input, sender: "User" }];
            setMessages(newMessages);
            onNewMessage(input);
            setInput('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div>
            <div style={{ height: '300px', overflowY: 'scroll', border: '1px solid #ddd', padding: '10px', marginBottom: '10px' }}>
                {messages.map((msg, index) => (
                    <div key={index} style={{ padding: '5px 0' }}>
                        <strong>{msg.sender}: </strong>{msg.text}
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}  // Handle Enter key
                style={{ width: '80%', padding: '5px' }}
                placeholder="Type a message..."
            />
            <button onClick={handleSend} style={{ padding: '5px', marginLeft: '5px' }}>Send</button>
        </div>
    );
}

export default Chat;