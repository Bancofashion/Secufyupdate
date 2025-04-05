"use client";

import { useEffect, useState } from "react";

export default function Chat() {
    const [ws, setWs] = useState(null);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const username = "user" + Math.floor(Math.random() * 1000); // Random naam voor test

    useEffect(() => {
        const websocket = new WebSocket(`ws://localhost:8000/chat/ws/${username}`);

        websocket.onmessage = (event) => {
            setMessages((prev) => [...prev, event.data]);
        };

        setWs(websocket);
        return () => websocket.close();
    }, []);

    const sendMessage = () => {
        if (ws && input.trim() !== "") {
            ws.send(input);
            setInput("");
        }
    };

    return (
        <div>
            <h1>Chat</h1>
            <div style={{ border: "1px solid #ccc", height: "300px", overflowY: "auto" }}>
                {messages.map((msg, index) => (
                    <div key={index}>{msg}</div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type een bericht..."
            />
            <button onClick={sendMessage}>Verstuur</button>
        </div>
    );
}
