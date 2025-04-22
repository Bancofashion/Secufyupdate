export async function apiRequest(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    data: any = null,
    isFormData: boolean = false
) {
    console.log(`[API] ${method} ${endpoint} met data:`, data);

    let token: string | null = null;
    if (typeof window !== "undefined") {
        token = localStorage.getItem('token');
    }

    const headers: HeadersInit = isFormData
        ? { "Content-Type": "application/x-www-form-urlencoded" }
        : { "Content-Type": "application/json" };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const options: RequestInit = {
        method,
        headers,
        body: isFormData ? data.toString() : data ? JSON.stringify(data) : null,
    };

    try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://secufy-backend.onrender.com";
        console.log(`[API] ${method} ${API_URL}${endpoint} wordt verzonden...`);

        const response = await fetch(`${API_URL}${endpoint}`, options);
        console.log(`[API RESPONSE] Status: ${response.status}`);

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            console.error(`[API ERROR] ${response.status}:`, errorData || response.statusText);
            throw new Error(`API Error ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('🚨 API request error:', error);
        throw error;
    }
}
