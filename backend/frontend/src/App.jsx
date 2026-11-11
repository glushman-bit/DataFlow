import { useState } from 'react'
import './App.css'
import TableList from './components/TableList'
import Login from './components/Login'


function App() {
  const [activePage, setActivePage] = useState('tables')
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return Boolean(localStorage.getItem('access'))
  })

  function handleLogin(tokens) {
    localStorage.setItem('access', tokens.access)
    localStorage.setItem('refresh', tokens.refresh)

    setIsAuthenticated(true)
  }

  function handleLogout() {
    localStorage.removeItem('access')
    localStorage.removeItem('refresh')

    setIsAuthenticated(false)
  }

  return (
      <>
        {!isAuthenticated ? (
            <Login onLogin={handleLogin} />
        ) : (
            <div className="app">
              <header className="header">
                <h1>DataFlow</h1>
                <span>Универсальная система пользовательских таблиц</span>

                <button onClick={handleLogout}>
                  Выйти
                </button>
              </header>

              <div className="main">
                <aside className="sidebar">
                  <h2>Навигация</h2>
                  <nav>
                    <ul>
                      <li
                          className={activePage === 'tables' ? 'active' : ''}
                          onClick={() => setActivePage('tables')}
                      >
                        Мои таблицы
                      </li>

                      <li
                          className={activePage === 'settings' ? 'active' : ''}
                          onClick={() => setActivePage('settings')}
                      >
                        Настройки
                      </li>
                    </ul>
                  </nav>
                </aside>

                <main className="content">
                  {activePage === 'tables' && <TableList/>}

                  {activePage === 'settings' && (
                      <>
                        <h2>Настройки</h2>
                        <p>Здесь будут настройки пользователя.</p>
                      </>
                  )}
                </main>
              </div>
            </div>
        )}
      </>
  )
}

export default App
