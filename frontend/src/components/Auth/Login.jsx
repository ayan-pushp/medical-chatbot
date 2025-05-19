import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Link } from 'react-router-dom';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    try {
      const success = await login(username, password);
      if (success) {
        setSuccessMessage(`Welcome, ${username}! Redirecting...`);
        setTimeout(() => navigate('/'), 3000); 
      }
    } catch (err) {
      const message = err.message || 'Login failed';
      setError(message);
      setTimeout(() => navigate('/'), 3000);
    }
  };

  return (
    <div className="auth-container">
      <h2>Login</h2>

      {error && <div className="error">{error}</div>}
      {successMessage ? (
       <div className="success">
        <p>{successMessage}</p>
        </div>

      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Username"
          required
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          required
        />
        <button type="submit">Login</button>
      </form>
      )}

      {!successMessage && (
        <div className="toggle-auth">
        Don't have an account? <Link to="/register">Register</Link>
      </div>
    )}
    </div>
  );
}
