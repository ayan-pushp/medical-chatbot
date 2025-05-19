import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    try {
      const response = await register(username, password);
      setSuccessMessage(response.message || 'Registration successful!');
    } catch (err) {
      setError('Registration failed. Username may be taken.');
    }
  };

  const handleGoToLogin = () => {
    navigate('/login');
  };

  return (
    <div className="auth-container">
      <h2>Register</h2>

      {error && <div className="error">{error}</div>}
      {successMessage ? (
        <div className="success">
          <p>{successMessage}!</p> <p> Login to start chatting.</p>
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
          <button type="submit">Register</button>
        </form>
      )}

      {!successMessage && (
        <div className="toggle-auth">
          Already have an account? <Link to="/login">Login</Link>
        </div>
      )}
    </div>
  );
}
