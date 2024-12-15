import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './login';

function App() {
  const [score, setScore] = useState(5);
  const [postResponse, setPostResponse] = useState('');
  const [token, setToken] = useState('');

  useEffect(() => {
    if (token) {
      fetchScores();
    }
  }, [token]);

  const fetchScores = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:8000/scores', {
        headers: { Authorization: `Bearer ${token}` }
      });
      console.log(response.data); // Puedes manejar las puntuaciones aquí si es necesario
    } catch (error) {
      console.error('Error fetching scores:', error);
    }
  };

  const handlePostScore = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/scores', {
        username: 'current_user', // Reemplaza con el nombre de usuario actual
        score: score
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPostResponse('¡Puntuación agregada!');
    } catch (error) {
      console.error('Error posting score:', error);
      setPostResponse('Error al agregar la puntuación.');
    }
  };

  const handleLogout = () => {
    setToken('');
    setPostResponse('');
  };

  if (!token) {
    return <Login setToken={setToken} />;
  }

  return (
    <div>
      <h1>¿Cómo te sientes de 0 a 10?</h1>
      <input
        type="range"
        min="0"
        max="10"
        value={score}
        onChange={(e) => setScore(e.target.value)}
      />
      <p>Puntuación: {score}</p>
      <button onClick={handlePostScore}>Enviar Puntuación</button>
      {postResponse && <p>{postResponse}</p>}
      <button onClick={handleLogout}>Desloguearse</button>
    </div>
  );
}

export default App;