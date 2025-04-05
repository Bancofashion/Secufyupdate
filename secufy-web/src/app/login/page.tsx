"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            router.push("/dashboard");
        }
    }, []);

    const handleLogin = async () => {
        setLoading(true);
        setError("");

        try {
            const response = await fetch("http://127.0.0.1:8080/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username,
                    password
                })
            });

            if (!response.ok) {
                throw new Error("Inloggen mislukt. Controleer je gebruikersnaam en wachtwoord.");
            }

            const data = await response.json();
            localStorage.setItem("token", data.access_token);

            // Haal gebruikersgegevens op
            const userResponse = await fetch("http://127.0.0.1:8080/users/me", {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${data.access_token}`
                }
            });

            if (!userResponse.ok) {
                throw new Error("Gebruikersgegevens ophalen mislukt.");
            }

            const userData = await userResponse.json();
            localStorage.setItem("user", JSON.stringify(userData));

            router.push("/dashboard");
        } catch (error: any) {
            setError(error.message || "Er is een fout opgetreden.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="p-6 bg-white shadow-md rounded-lg">
                <h2 className="text-2xl font-semibold mb-4">Inloggen</h2>

                {error && <p className="text-red-500">{error}</p>}

                <input
                    type="text"
                    placeholder="Gebruikersnaam"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full p-2 border rounded mb-2"
                />
                <input
                    type="password"
                    placeholder="Wachtwoord"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full p-2 border rounded mb-2"
                />

                <button
                    onClick={handleLogin}
                    className="w-full bg-blue-500 text-white p-2 rounded mt-2"
                    disabled={loading}
                >
                    {loading ? "Bezig met inloggen..." : "Inloggen"}
                </button>
            </div>
        </div>
    );
}
