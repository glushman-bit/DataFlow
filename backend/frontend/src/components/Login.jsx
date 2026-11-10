import { useState } from 'react'
import { login } from '../api/tables'


function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()

    try {
      const data = await login(username, password)

      onLogin(data)
    } catch (error) {
      console.error(error.message)
    }
  }

  return (
    <div className="login">
      <h2>Вход в DataFlow</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Имя пользователя"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
        />

        <input
          type="password"
          placeholder="Пароль"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
        />

        <button type="submit">
          Войти
        </button>
      </form>
    </div>
  )
}

export default Login