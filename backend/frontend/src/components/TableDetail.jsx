import { useState, useEffect } from "react";
import {
  getFields,
  createField,
  getRecords,
  createRecord,
  updateRecord,
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
  const [editingRecordId, setEditingRecordId] = useState(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [newFieldRequired, setNewFieldRequired] = useState(true)
  const [newFieldSettings, setNewFieldSettings] = useState({})
  const [fieldErrors, setFieldErrors] = useState({})
  const [editFieldErrors, setEditFieldErrors] = useState({})
  const [editError, setEditError] = useState('')



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
      required: newFieldRequired,
      order: fields.length,
      settings: newFieldSettings,
    }

    try {
      const token = localStorage.getItem('access')
      const newField = await createField(table.id, fieldData, token)

      setFields([...fields, newField])
      setNewFieldName('')
      setNewFieldLabel('')
      setNewFieldType('text')
      setNewFieldRequired(true)
      setNewFieldSettings({})
      setError('')
    } catch (error) {
      setError(error.message)
    }
  }

  function getInputType(fieldType) {
    const inputTypes = {
      text: 'text',
      integer: 'number',
      decimal: 'number',
      date: 'date',
      datetime: 'datetime-local',
    }

    return inputTypes[fieldType] || 'text'
  }

  function handleRecordChange(fieldName, value) {
    setNewRecordValues((prev) => ({
      ...prev,
      [fieldName]: value,
    }))

    setFieldErrors((prev) => {
      const updatedErrors = { ...prev }
      delete updatedErrors[fieldName]
      return updatedErrors
    })

    setEditFieldErrors((prev) => {
      const updatedErrors = { ...prev }
      delete updatedErrors[fieldName]
      return updatedErrors
    })
  }

  function handleTypedRecordChange(field, value) {
    if (field.field_type === 'boolean') {
      handleRecordChange(
        field.name,
        value === '' ? '' : value === 'true'
      )
      return
    }

    handleRecordChange(field.name, value)
  }

  function handleEditRecord(record) {
    setEditingRecordId(record.id)
    setNewRecordValues({ ...record.values })
    setEditFieldErrors({})
    setEditError('')
    setError('')
    setIsEditModalOpen(true)
  }

  async function handleAddRecord() {
    try {
      const token = localStorage.getItem('access')

      setError('')
      setFieldErrors({})

      const newRecord = await createRecord(table.id, newRecordValues, token)

      setRecords([...records, newRecord])
      setNewRecordValues({})
    } catch (error) {
      if (error.details?.values) {
        setFieldErrors(error.details.values)
      } else {
        setError(error.message)
      }
    }
  }

  async function handleUpdateRecord() {
    try {
      setEditFieldErrors({})
      setEditError('')

      const updatedRecord = await updateRecord(
        table.id,
        editingRecordId,
        newRecordValues
      )

      setRecords(
        records.map((record) =>
          record.id === editingRecordId
            ? updatedRecord
            : record
        )
      )

      setEditingRecordId(null)
      setNewRecordValues({})
      setIsEditModalOpen(false)
      setError('')

    } catch (error) {
      if (error.details?.values) {
        setEditFieldErrors(error.details.values)
      } else {
        setEditError(error.message)
      }
    }
  }

  function handleCancelEdit() {
    setIsEditModalOpen(false)
    setEditingRecordId(null)
    setNewRecordValues({})
    setEditFieldErrors({})
    setEditError('')
    setError('')
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
          <option value="integer">Целое число</option>
          <option value="decimal">Десятичное число</option>
          <option value="date">Дата</option>
          <option value="datetime">Дата и время</option>
          <option value="boolean">Да / Нет</option>
        </select>

        <label className="field-required">
          <input
            type="checkbox"
            checked={newFieldRequired}
            onChange={(event) => setNewFieldRequired(event.target.checked)}
          />
          Обязательное поле
        </label>

        {newFieldType === 'integer' && (
          <div className="field-settings">
            <input
              type="number"
              placeholder="Минимальное значение"
              value={newFieldSettings.min ?? ''}
              onChange={(event) => {
                const value = event.target.value

                setNewFieldSettings((prev) => ({
                  ...prev,
                  min: value === '' ? undefined : value,
                }))
              }}
            />

            <input
              type="number"
              placeholder="Максимальное значение"
              value={newFieldSettings.max ?? ''}
              onChange={(event) => {
                const value = event.target.value

                setNewFieldSettings((prev) => ({
                  ...prev,
                  max: value === '' ? undefined : value,
                }))
              }}
            />
          </div>
        )}

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

      <p className="required-hint">
        <span className="required-mark">*</span> — обязательное поле
      </p>

      <div className="record-form">
        {fields.map((field) => (
          <div className="form-group" key={field.id}>

            <label>
              {field.label}
              {field.required && (
                <span className="required-mark"> *</span>
              )}
            </label>

            {field.field_type === 'boolean' ? (
              <select
                value={
                  newRecordValues[field.name] === undefined ||
                  newRecordValues[field.name] === ''
                    ? ''
                    : String(newRecordValues[field.name])
                }
                className={fieldErrors[field.name] ? 'input-error' : ''}
                onChange={(event) =>
                  handleTypedRecordChange(field, event.target.value)
                }
              >
                <option value="">Выберите значение</option>
                <option value="true">Да</option>
                <option value="false">Нет</option>
              </select>
            ) : (

              <input
                type={getInputType(field.field_type)}
                step={
                  field.field_type === 'integer'
                    ? 1
                    : field.field_type === 'decimal'
                      ? 'any'
                      : undefined
                }
                min={field.settings?.min}
                max={field.settings?.max}
                value={newRecordValues[field.name] ?? ''}
                className={fieldErrors[field.name] ? 'input-error' : ''}
                onChange={(event) =>
                  handleTypedRecordChange(field, event.target.value)
                }
              />
            )}

            {fieldErrors[field.name] && (
              <p className="field-error">
                {fieldErrors[field.name][0]}
              </p>
            )}
          </div>
        ))}

        <button onClick={handleAddRecord}>
          Добавить запись
        </button>

        {editingRecordId !== null && (
          <button
            onClick={() => {
              setEditingRecordId(null)
              setNewRecordValues({})
            }}
          >
            Отмена
          </button>
        )}
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
                    {field.field_type === 'boolean'
                      ? record.values[field.name] === true
                        ? 'Да'
                        : record.values[field.name] === false
                          ? 'Нет'
                          : ''
                      : record.values[field.name]}
                  </td>
                ))}

                <td>
                  <button
                    className="edit-button"
                    onClick={() => handleEditRecord(record)}
                    title="Редактировать запись"
                  >
                    ✎
                  </button>

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


    {isEditModalOpen && (
      <div className="modal-overlay">
        <div className="modal">
          <h3>Редактирование записи</h3>

          <div className="record-form modal-record-form">
            {editError && (
              <p className="field-error">{editError}</p>
            )}

            {fields.map((field) => (
              <div className="form-group" key={field.id}>
                <label>
                  {field.label}
                  {field.required && (
                    <span className="required-mark"> *</span>
                  )}
                </label>

                {field.field_type === 'boolean' ? (
                  <select
                    value={
                      newRecordValues[field.name] === undefined ||
                      newRecordValues[field.name] === ''
                        ? ''
                        : String(newRecordValues[field.name])
                    }
                    className={
                      editFieldErrors[field.name] ? 'input-error' : ''
                    }
                    onChange={(event) =>
                      handleTypedRecordChange(field, event.target.value)
                    }
                  >
                    <option value="">Выберите значение</option>
                    <option value="true">Да</option>
                    <option value="false">Нет</option>
                  </select>
                ) : (
                  <input
                    type={getInputType(field.field_type)}
                    step={
                      field.field_type === 'integer'
                        ? 1
                        : field.field_type === 'decimal'
                          ? 'any'
                          : undefined
                    }
                    min={field.settings?.min}
                    max={field.settings?.max}
                    value={newRecordValues[field.name] ?? ''}
                    className={
                      editFieldErrors[field.name] ? 'input-error' : ''
                    }
                    onChange={(event) =>
                      handleTypedRecordChange(field, event.target.value)
                    }
                  />
                )}

                {editFieldErrors[field.name] && (
                  <p className="field-error">
                    {editFieldErrors[field.name][0]}
                  </p>
                )}
              </div>
            ))}
          </div>

          <div className="modal-actions">
            <button
              className="cancel-button"
              onClick={handleCancelEdit}
            >
              Отмена
            </button>

            <button
              className="save-button"
              onClick={handleUpdateRecord}
            >
              Сохранить
            </button>
          </div>
        </div>
      </div>
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
