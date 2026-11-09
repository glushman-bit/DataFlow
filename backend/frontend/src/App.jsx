import './App.css'

function App() {
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
              <li>Мои таблицы</li>
              <li>Настройки</li>
          </ul>
          </nav>
        </aside>

        <main className="content">
          <h2>Мои таблицы</h2>
          <p>Здесь будут отображаться ваши таблицы.</p>
        </main>
      </div>
    </div>
  )
}

export default App
