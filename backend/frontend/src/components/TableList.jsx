import { useState, useEffect } from 'react'
import TableDetail from './TableDetail'
import { getTables, createTable } from '../api/tables'


function TableList() {
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState(null)
  const [newTableName, setNewTableName] = useState('')

  useEffect(() => {
    async function loadTables() {
      try {
        const token = localStorage.getItem('access')
        const data = await getTables(token)

        setTables(data)
      } catch (error) {
        console.error(error.message)
      }
    }

    loadTables()
  }, [])

  if (selectedTable) {
    return (
      <TableDetail
        table={selectedTable}
        onBack={() => setSelectedTable(null)}
      />
    )
  }

  async function handleAddTable() {
    const name = newTableName.trim()

    if (!name) {
      return
    }

    try {
      const token = localStorage.getItem('access')
      const newTable = await createTable(name, token)

      setTables([...tables, newTable])
      setNewTableName('')
    } catch (error) {
      console.error(error.message)
    }
  }

  return (
    <div className="table-list">
      <h2>Мои таблицы</h2>

      <div className="table-form">
        <input
          type="text"
          placeholder="Название новой таблицы"
          value={newTableName}
          onChange={(event) => setNewTableName(event.target.value)}
        />
        <button onClick={handleAddTable}>
          Создать таблицу
        </button>
      </div>

      <div className="table-grid">
        {tables.map((table) => (
        <div
          className="table-card"
          key={table.id}
          onClick={() => setSelectedTable(table)}
        >
          {table.name}
        </div>
        ))}
      </div>
    </div>
  )
}

export default TableList
