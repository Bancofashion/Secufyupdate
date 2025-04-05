import { useEffect, useState } from 'react';
import apiRequest from '../api/api';
import { useRouter } from 'next/router';

export default function Shifts() {
    const [shifts, setShifts] = useState([]);
    const [shiftDetails, setShiftDetails] = useState({ shift_date: '', start_time: '', end_time: '', location: '', employee_ids: '' });
    const router = useRouter();
    const [userRole, setUserRole] = useState('');

    useEffect(() => {
        fetchUserRole();
    }, []);

    const fetchUserRole = async () => {
        try {
            const user = await apiRequest('/users/me', 'GET');
            setUserRole(user.role);
            fetchShifts();
        } catch (error) {
            router.push('/login'); // 🚀 Niet-ingelogde gebruikers naar login
        }
    };

    const fetchShifts = async () => {
        const data = await apiRequest('/shifts', 'GET');
        setShifts(data);
    };

    const handleAddShift = async () => {
        await apiRequest('/shifts', 'POST', { ...shiftDetails, employee_ids: shiftDetails.employee_ids.split(',') });
        fetchShifts();
        setShiftDetails({ shift_date: '', start_time: '', end_time: '', location: '', employee_ids: '' });
    };

    const handleDeleteShift = async (id) => {
        await apiRequest(`/shifts/${id}`, 'DELETE');
        fetchShifts();
    };

    return (
        <div>
            <h1>Shifts Beheer</h1>
            {["admin", "planner"].includes(userRole) && (
                <>
                    <input value={shiftDetails.shift_date} onChange={(e) => setShiftDetails({ ...shiftDetails, shift_date: e.target.value })} placeholder="Datum (YYYY-MM-DD)" />
                    <input value={shiftDetails.start_time} onChange={(e) => setShiftDetails({ ...shiftDetails, start_time: e.target.value })} placeholder="Starttijd (HH:MM:SS)" />
                    <input value={shiftDetails.end_time} onChange={(e) => setShiftDetails({ ...shiftDetails, end_time: e.target.value })} placeholder="Eindtijd (HH:MM:SS)" />
                    <input value={shiftDetails.location} onChange={(e) => setShiftDetails({ ...shiftDetails, location: e.target.value })} placeholder="Locatie" />
                    <input value={shiftDetails.employee_ids} onChange={(e) => setShiftDetails({ ...shiftDetails, employee_ids: e.target.value })} placeholder="Medewerker ID's (comma-separated)" />
                    <button onClick={handleAddShift}>Shift Toevoegen</button>
                </>
            )}
            <ul>
                {shifts.map((shift) => (
                    <li key={shift.id}>
                        {shift.shift_date} {shift.start_time} - {shift.end_time} @ {shift.location}
                        {shift.employee_ids.length > 0 ? ` (Medewerkers: ${shift.employee_ids.join(', ')})` : ' (Open dienst)'}
                        {["admin", "planner"].includes(userRole) && (
                            <button onClick={() => handleDeleteShift(shift.id)}>Verwijder</button>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
}
