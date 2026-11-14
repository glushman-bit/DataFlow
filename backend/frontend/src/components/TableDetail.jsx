import { useState, useEffect } from "react";
import {
  getFields,
  createField,
  getRecords,
  createRecord,
  deleteRecord
} from '../api/tables'


function TableDetail({ table, onBack }) {
  const [fields, setFields] = useState([])
  const [records, setRecords] = useState([])
  const [error, setError] = useState('')
  const [newFieldName, setNewFieldName] = useState('')
  const [newFieldLabel, setNewFieldLabel] = useState('')
  const [newFieldType, setNewFieldType] = useState('text')
  const [newRecordValues, setNewRecordValues] = useState({})
  const [recordToDelete, setRecordToDelete] = useState(null)

  useEffect(() => {
    async function loadFields() {
      try {
        const token = localStorage.getItem('access')
        const data = await getFields(table.id, token)
        const recordsData = await getRecords(table.id, token)

        setFields(data)
        setRecords(recordsData)

      } catch (error) {
        setError(error.message)
      }
    }

    loadFields()
  }, [table.id])

  async function handleAddField() {
    const fieldData = {
      name: newFieldName.trim(),
      label: newFieldLabel.trim(),
      field_type: newFieldType,
      required: true,
      order: fields.length,
      settings: {},
    }

    try {
      const token = localStorage.getItem('access')
      const newField = await createField(table.id, fieldData, token)

      setFields([...fields, newField])
      setNewFieldName('')
      setNewFieldLabel('')
      setNewFieldType('text')
      setError('')
    } catch (error) {
      setError(error.message)
    }
  }

  function handleRecordChange(fieldName, value) {
    setNewRecordValues({
      ...newRecordValues,
      [fieldName]: value,
    })
  }

  async function handleAddRecord() {
    try {
      const token = localStorage.getItem('access')

      const newRecord = await createRecord(
        table.id,
        newRecordValues,
        token
      )

      setRecords([...records, newRecord])
      setNewRecordValues({})
      setError('')
    } catch (error) {
      setError(error.message)
    }
  }

  function handleDeleteRecord(recordId) {
    setRecordToDelete(recordId)
  }

  async function confirmDeleteRecord() {
    try {
      const token = localStorage.getItem('access')

      await deleteRecord(table.id, recordToDelete, token)

      setRecords(
        records.filter((record) => record.id !== recordToDelete)
      )

      setRecordToDelete(null)
      setError('')
    } catch (error) {
      setError(error.message)
    }
  }

  return (
    <div className="table-detail">
      <button onClick={onBack}>
        Назад к таблицам
      </button>

      <h2>{table.name}</h2>

      {error && <p>{error}</p>}

      <h3>Добавить поле</h3>

      <div className="field-form">
        <input
          type="text"
          placeholder="Техническое имя (например, client)"
          value={newFieldName}
          onChange={(event) => setNewFieldName(event.target.value)}
        />

        <input
          type="text"
          placeholder="Название поля (например, Клиент)"
          value={newFieldLabel}
          onChange={(event) => setNewFieldLabel(event.target.value)}
        />

        <select
          value={newFieldType}
          onChange={(event) => setNewFieldType(event.target.value)}
        >
          <option value="text">Текст</option>
          <option value="number">Число</option>
          <option value="date">Дата</option>
          <option value="boolean">Да / Нет</option>
        </select>

        <button onClick={handleAddField}>
          Добавить поле
        </button>
      </div>

      <h3>Поля таблицы</h3>

      {fields.length === 0 ? (
        <p>В таблице пока нет полей.</p>
      ) : (
        <ul>
          {fields.map((field) => (
            <li key={field.id}>
              {field.label}
            </li>
          ))}
        </ul>
      )}

      <h3>Добавить запись</h3>

      <div className="record-form">
        {fields.map((field) => (
          <input
            key={field.id}
            type="text"
            placeholder={field.label}
            value={newRecordValues[field.name] || ''}
            onChange={(event) =>
              handleRecordChange(field.name, event.target.value)
            }
          />
        ))}

        <button onClick={handleAddRecord}>
          Добавить запись
        </button>
      </div>

      <h3>Записи таблицы</h3>

      {records.length === 0 ? (
        <p>В таблице пока нет записей.</p>
      ) : (
        <table>
          <thead>
            <tr>
              {fields.map((field) => (
                <th key={field.id}>
                  {field.label}
                </th>
              ))}

              <th>Действия</th>
            </tr>
          </thead>

          <tbody>
            {records.map((record) => (
              <tr key={record.id}>
                {fields.map((field) => (
                  <td key={field.id}>
                    {record.values[field.name]}
                  </td>
                ))}
                <td>
                  <button
                    className="delete-button"
                    onClick={() => handleDeleteRecord(record.id)}
                    title="Удалить запись"
                  >
                    ×
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

    {recordToDelete !== null && (
      <div className="modal-overlay">
        <div className="modal">
          <h3>Удаление записи</h3>

          <p>Вы действительно хотите удалить эту запись?</p>

          <div className="modal-actions">
            <button
              className="cancel-button"
              onClick={() => setRecordToDelete(null)}
            >
              Отмена
            </button>

            <button
              className="confirm-button"
              onClick={confirmDeleteRecord}
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    )}

    </div>
  )
}

export default TableDetail
