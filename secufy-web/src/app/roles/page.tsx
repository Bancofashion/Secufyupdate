"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import apiRequest from '@/lib/api';

export default function Roles() {
    const [roles, setRoles] = useState([]);
    const [roleName, setRoleName] = useState('');
    const [permissions, setPermissions] = useState('');
    const router = useRouter();
    const [userRole, setUserRole] = useState('');

    useEffect(() => {
        fetchUserRole();
    }, []);

    const fetchUserRole = async () => {
        try {
            const user = await apiRequest('/users/me', 'GET');
            setUserRole(user.role);
            if (user.role !== 'admin') {
                router.push('/dashboard'); // 🚀 Stuurt niet-admins terug naar dashboard
            } else {
                fetchRoles();
            }
        } catch (error) {
            router.push('/login'); // 🚀 Stuurt niet-ingelogde gebruikers naar login
        }
    };

    const fetchRoles = async () => {
        const data = await apiRequest('/roles', 'GET');
        setRoles(Object.entries(data));
    };

    return userRole === 'admin' ? (
        <div>
            <h1>Rolbeheer (Admin Only)</h1>
            {/* Overige UI-code blijft ongewijzigd */}
        </div>
    ) : null;
}
