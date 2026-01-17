'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Mock Authentication
    setTimeout(() => {
        router.push('/dashboard');
    }, 1500);
  };

  return (
    <div style={{
        height: '100vh',
        width: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        color: 'white',
        fontFamily: 'Inter, sans-serif'
    }}>
        <div style={{
            width: '400px',
            padding: '3rem',
            background: 'rgba(255, 255, 255, 0.03)',
            backdropFilter: 'blur(20px)',
            borderRadius: '24px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
        }}>
            <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
                <h1 style={{ 
                    fontSize: '2rem', 
                    fontWeight: 'bold', 
                    marginBottom: '0.5rem',
                    background: 'linear-gradient(to right, #fff, #888)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent'
                }}>ControlGastos</h1>
                <p style={{ color: '#666', fontSize: '0.9rem' }}>Enterprise Access Portal</p>
            </div>

            <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem', color: '#888' }}>CORPORATE ID / EMAIL</label>
                    <input 
                        type="email" 
                        required 
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="admin@enterprise.com"
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: 'rgba(0,0,0,0.3)',
                            border: '1px solid #333',
                            borderRadius: '12px',
                            color: 'white',
                            outline: 'none',
                            transition: 'all 0.3s ease'
                        }}
                    />
                </div>
                
                <div>
                    <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.8rem', color: '#888' }}>PASSWORD</label>
                    <input 
                        type="password" 
                        required 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••••••"
                        style={{
                            width: '100%',
                            padding: '1rem',
                            background: 'rgba(0,0,0,0.3)',
                            border: '1px solid #333',
                            borderRadius: '12px',
                            color: 'white',
                            outline: 'none'
                        }}
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={isLoading}
                    style={{
                        marginTop: '1rem',
                        padding: '1rem',
                        background: 'white',
                        color: 'black',
                        border: 'none',
                        borderRadius: '12px',
                        fontWeight: 'bold',
                        cursor: isLoading ? 'wait' : 'pointer',
                        opacity: isLoading ? 0.7 : 1,
                        transition: 'transform 0.1s ease'
                    }}
                >
                    {isLoading ? 'AUTHENTICATING...' : 'SECURE LOGIN →'}
                </button>
            </form>
            
            <div style={{ marginTop: '2rem', textAlign: 'center', fontSize: '0.75rem', color: '#444' }}>
                SECURED BY ANTIGRAVITY ENCRYPTION
            </div>
        </div>
    </div>
  );
}
