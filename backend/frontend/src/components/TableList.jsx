import { useState, useEffect } from 'react'
import TableDetail from './TableDetail'
import { getTables, createTable, deleteTable } from '../api/tables'


function TableList() {
  const [tables, setTables] = useState([])
  const [selectedTable, setSelectedTable] = useState(null)
  const [newTableName, setNewTableName] = useState('')
  const [newTableDescription, setNewTableDescription] = useState('')
  const [tableToDelete, setTableToDelete] = useState(null)

  useEffect(() => {
    async function loadTables() {
      try {
        const data = await getTables()

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
      const description = newTableDescription.trim()
      const newTable = await createTable(name, description)

      setTables([...tables, newTable])
      setNewTableName('')
      setNewTableDescription('')

    } catch (error) {
      console.error(error.message)
    }
  }

  async function handleDeleteTable() {
    if (!tableToDelete) {
      return
    }

    try {
      await deleteTable(tableToDelete.id)

      setTables((prevTables) =>
        prevTables.filter((table) => table.id !== tableToDelete.id)
      )

      setTableToDelete(null)
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

        <textarea
          placeholder="Описание таблицы (необязательно)"
          value={newTableDescription}
          onChange={(event) => setNewTableDescription(event.target.value)}
        />

        <button onClick={handleAddTable}>
          Создать таблицу
        </button>
      </div>

      <div className="tables-list">
        <div className="tables-header">
          <span>Название таблицы</span>
          <span>Описание</span>
          <span>Действия</span>
        </div>

        {tables.map((table) => (
          <div className="table-row" key={table.id}>
            <span
              className="table-name"
              onClick={() => setSelectedTable(table)}
            >
              {table.name}
            </span>

            <span className="table-description">
              {table.description || '—'}
            </span>

            <div className="table-actions">
              <button
                className="delete-button"
                onClick={(event) => {
                  event.stopPropagation()
                  setTableToDelete(table)
                }}
                title="Удалить запись"
              >
                ×
              </button>
            </div>
          </div>
        ))}

        {tableToDelete && (
          <div className="modal-overlay">
            <div className="modal">
              <h3>Удаление таблицы</h3>

              <p>
                Вы действительно хотите удалить таблицу
                «{tableToDelete.name}»?
              </p>

              <div className="modal-actions">
                <button
                  className="cancel-button"
                  onClick={() => setTableToDelete(null)}
                >
                  Отмена
                </button>

                <button
                  className="confirm-button"
                  onClick={handleDeleteTable}
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        )}


      </div>



    </div>
  )
}

export default TableList
