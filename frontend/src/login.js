import React, { useState } from 'react';
import axios from 'axios';

function Login({ setToken }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isRegister) {
        await axios.post('http://127.0.0.1:8000/register', { username, password });
        setMessage('Usuario registrado con éxito. Ahora puedes iniciar sesión.');
        setIsRegister(false); // Cambia a modo de inicio de sesión después del registro
      } else {
        const response = await axios.post('http://127.0.0.1:8000/token', new URLSearchParams({
          username,
          password
        }));
        setToken(response.data.access_token);
      }
    } catch (error) {
      setMessage('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div>
      <h1>{isRegister ? 'Registro' : 'Login'}</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Nombre de usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button type="submit">{isRegister ? 'Registrar' : 'Iniciar sesión'}</button>
      </form>
      <button onClick={() => setIsRegister(!isRegister)}>
        {isRegister ? '¿Ya tienes una cuenta? Inicia sesión' : '¿No tienes una cuenta? Regístrate'}
      </button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Login;