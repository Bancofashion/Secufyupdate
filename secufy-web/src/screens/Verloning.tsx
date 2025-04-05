import { useEffect, useState } from 'react';
import apiRequest from '../api/api';
import { useRouter } from 'next/router';

export default function Verloning() {
    const [payrolls, setPayrolls] = useState([]);
    const [uploads, setUploads] = useState([]);
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
            fetchPayrolls();
            fetchUploads();
        } catch (error) {
            router.push('/login');
        }
    };

    const fetchPayrolls = async () => {
        const data = await apiRequest('/verloning', 'GET');
        setPayrolls(data);
    };

    const fetchUploads = async () => {
        const data = await apiRequest('/verloning/uploads', 'GET');
        setUploads(data.loonstroken);
    };

    const handleFileChange = (event) => {
        setSelectedFile(event.target.files[0]);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        const formData = new FormData();
        formData.append("file", selectedFile);

        await fetch('/api/verloning/upload', {
            method: 'POST',
            body: formData
        });

        alert("Loonstrook geüpload!");
        fetchUploads();
    };

    const handleDownload = async (filename) => {
        window.open(`/api/verloning/download/${filename}`, '_blank');
    };

    return (
        <div>
            <h1>Verloning Overzicht</h1>
            <input type="file" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload Loonstrook</button>

            <h2>Geüploade Loonstroken</h2>
            <ul>
                {uploads.map((file) => (
                    <li key={file}>
                        {file} <button onClick={() => handleDownload(file)}>Download</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
