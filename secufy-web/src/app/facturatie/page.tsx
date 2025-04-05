"use client";

import { useEffect, useState } from 'react';
import apiRequest from '@/lib/api';
import { useRouter } from 'next/navigation';

export default function Facturatie() {
    const [facturen, setFacturen] = useState([]);
    const [selectedFile, setSelectedFile] = useState(null);
    const router = useRouter();
    const [user, setUser] = useState(null);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const userData = await apiRequest('/users/me', 'GET');
            if (!["admin", "boekhouding"].includes(userData.role)) {
                router.push('/');
            }
            setUser(userData);
            fetchFacturen();
        } catch (error) {
            router.push('/login');
        }
    };

    const fetchFacturen = async () => {
        const data = await apiRequest('/facturen/uploads', 'GET');
        setFacturen(data.facturen);
    };

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        const formData = new FormData();
        formData.append("file", selectedFile);

        await fetch('/api/facturen/upload', {
            method: 'POST',
            body: formData
        });

        alert("Factuur geüpload!");
        fetchFacturen();
    };

    const handleDownload = async (filename) => {
        window.open(`/api/facturen/download/${filename}`, '_blank');
    };

    return (
        <div>
            <h1>Facturatie Overzicht</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload Factuur</button>

            <h2>Geüploade Facturen</h2>
            <ul>
                {facturen.map((file) => (
                    <li key={file}>
                        {file} <button onClick={() => handleDownload(file)}>Download</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
