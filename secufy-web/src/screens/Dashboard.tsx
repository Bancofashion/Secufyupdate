import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { apiRequest } from '@/lib/api';

export default function Dashboard() {
    const [user, setUser] = useState(null);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            router.push('/login');
            return;
        }

        const fetchUser = async () => {
            try {
                const data = await apiRequest('/users/me');
                setUser(data);
            } catch (error) {
                localStorage.removeItem('token');
                router.push('/login');
            }
        };
        fetchUser();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/login');
    };

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="p-6 bg-white shadow-md rounded-lg">
                <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>
                {user ? <p>Welkom, {user.name}!</p> : <p>Gebruikersgegevens laden...</p>}
                <button
                    onClick={handleLogout}
                    className="w-full bg-red-500 text-white p-2 rounded mt-4">
                    Uitloggen
                </button>
            </div>
        </div>
    );
}
