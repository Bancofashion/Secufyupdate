import { useEffect, useState } from 'react';
import apiRequest from '../api/api';
import { useRouter } from 'next/router';

export default function OpenShifts() {
    const [shifts, setShifts] = useState([]);
    const router = useRouter();
    const [user, setUser] = useState(null);

    useEffect(() => {
        fetchUser();
    }, []);

    const fetchUser = async () => {
        try {
            const userData = await apiRequest('/users/me', 'GET');
            setUser(userData);
            fetchShifts();
        } catch (error) {
            router.push('/login'); // 🚀 Niet-ingelogde gebruikers naar login
        }
    };

    const fetchShifts = async () => {
        const data = await apiRequest('/shifts/open/diensten', 'GET');
        setShifts(data);
    };

    const handleJoinShift = async (shiftId) => {
        await apiRequest(`/shifts/${shiftId}/join`, 'POST');
        alert('Je bent ingeschreven voor de dienst! Je ontvangt een bevestigingsmail.');
        fetchShifts();
    };

    const handleLeaveShift = async (shiftId) => {
        await apiRequest(`/shifts/${shiftId}/leave`, 'POST');
        alert('Je bent uitgeschreven voor de dienst! Je ontvangt een bevestigingsmail.');
        fetchShifts();
    };

    return (
        <div>
            <h1>Open Diensten</h1>
            <ul>
                {shifts.map((shift) => (
                    <li key={shift.id}>
                        {shift.shift_date} {shift.start_time} - {shift.end_time} @ {shift.location}
                        {shift.employee_ids.length > 0 ? ` (Medewerkers: ${shift.employee_ids.join(', ')})` : ' (Open dienst)'}
                        {shift.employee_ids.includes(user?.username) ? (
                            <button onClick={() => handleLeaveShift(shift.id)}>Uitschrijven</button>
                        ) : (
                            <button onClick={() => handleJoinShift(shift.id)}>Inschrijven</button>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}
