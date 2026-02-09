class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:8000';
        this.token = localStorage.getItem('token');
        console.log('API Service initialized, token:', this.token ? 'present' : 'absent');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
        console.log('Token set:', token.substring(0, 20) + '...');
    }

    removeToken() {
        this.token = null;
        localStorage.removeItem('token');
        console.log('Token removed');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        console.log(`API Request: ${options.method || 'GET'} ${url}`);
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
            console.log('Adding Authorization header');
        }

        const config = {
            ...options,
            headers,
        };

        if (options.body instanceof FormData) {
            delete headers['Content-Type'];
        }

        try {
            const response = await fetch(url, config);
            console.log(`Response status: ${response.status}`);
            
            const responseText = await response.text();
            console.log('Response text:', responseText.substring(0, 200));
            
            let data;
            try {
                data = responseText ? JSON.parse(responseText) : {};
            } catch (e) {
                console.error('Failed to parse JSON:', responseText);
                data = {};
            }

            if (!response.ok) {
                console.error('API Error:', data);
                if (response.status === 401) {
                    this.removeToken();
                    window.location.href = '/login';
                }
                throw new Error(data.detail || data.error || `Ошибка ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    }

    async register(userData) {
        console.log('Registering user:', userData);
        return this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });
    }

    async login(email, password) {
        console.log('Logging in with:', email);
        return this.request('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
        });
    }

    async getProfile() {
        console.log('Getting profile');
        return this.request('/me');
    }

    async getStandards() {
        return this.request('/');
    }

    async getStandardById(id) {
        return this.request(`/${id}`);
    }

    async createStandard(standardData) {
        return this.request('/uploadstandard', {
            method: 'POST',
            body: JSON.stringify(standardData),
        });
    }

    async uploadDocument(file) {
        const formData = new FormData();
        formData.append('file', file);

        return this.request('/uploaddocument/', {
            method: 'POST',
            body: formData,
        });
    }
}

export const api = new ApiService();