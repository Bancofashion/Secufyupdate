import { useEffect, useState } from 'react';
import apiRequest from '../api/api';
import { useRouter } from 'next/router';

export default function DienstAanvragen() {
    const [requests, setRequests] = useState([]);
    const router = useRouter();
    const [user, setUser] = useState(null);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const userData = await apiRequest('/users/me', 'GET');
            if (!["admin", "planner"].includes(userData.role)) {
                router.push('/'); // Alleen admins/planners mogen deze pagina zien
            }
            setUser(userData);
            fetchRequests();
        } catch (error) {
            router.push('/login');
        }
    };

    const fetchRequests = async () => {
        const data = await apiRequest('/dienstaanvragen/open', 'GET');
        setRequests(data);
    };

    const handleApprove = async (id) => {
        await apiRequest(`/dienstaanvragen/${aanvraag_id}/approve`, 'POST');
        fetchRequests();
    };

    const handleReject = async (id) => {
        await apiRequest(`/dienstaanvragen/${aanvraag_id}/reject`, 'POST');
        fetchRequests();
    };

    return (
        <div>
            <h1>Dienstaanvragen</h1>
            <ul>
                {requests.map((request) => (
                    <li key={request.id}>
                        {request.employee} heeft een dienst aangevraagd op {request.date}
                        <button onClick={() => handleApprove(request.id)}>Goedkeuren</button>
                        <button onClick={() => handleReject(request.id)}>Weigeren</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
