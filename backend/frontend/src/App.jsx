import { useState } from 'react'
import './App.css'


function App() {
  const [activePage, setActivePage] = useState('tables')
  return (
    <div className="app">
      <header className="header">
        <h1>DataFlow</h1>
        <span>Универсальная система пользовательских таблиц</span>
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
          {activePage === 'tables' && (
            <>
              <h2>Мои таблицы</h2>
              <p>Здесь будут отображаться ваши таблицы.</p>
            </>
          )}

          {activePage === 'settings' && (
            <>
              <h2>Настройки</h2>
              <p>Здесь будут настройки пользователя.</p>
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
