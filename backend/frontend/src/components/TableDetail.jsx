import { useState, useEffect } from "react";
import {
  getFields,
  deleteField,
  getRecords,
  getOverdueRecords,
  createRecord,
  updateRecord,
  deleteRecord
} from '../api/tables'


function getCurrentDateTime(fieldType) {
    const now = new Date()

    if (fieldType === 'date') {
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')

      return `${year}-${month}-${day}`
    }

    if (fieldType === 'datetime') {
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hours = String(now.getHours()).padStart(2, '0')
      const minutes = String(now.getMinutes()).padStart(2, '0')

      return `${year}-${month}-${day}T${hours}:${minutes}`
    }

    return ''
  }

function formatDateTime(value) {
    if (!value) return ''

    const date = new Date(value)

    if (Number.isNaN(date.getTime())) {
      return value
    }

    return date.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

function getInitialRecordValues(fields) {
  const values = {}

  fields.forEach(field => {
    if (
      field.settings?.auto_now &&
      (field.field_type === 'date' || field.field_type === 'datetime')
    ) {
      values[field.name] = getCurrentDateTime(field.field_type)
    }
  })

  return values
}

function TableDetail({ table, onBack }) {
  const [fields, setFields] = useState([])
  const [records, setRecords] = useState([])
  const [overdueRecords, setOverdueRecords] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isAddingRecord, setIsAddingRecord] = useState(false)
  const [isUpdatingRecord, setIsUpdatingRecord] = useState(false)
  const [isDeletingField, setIsDeletingField] = useState(false)
  const [newRecordValues, setNewRecordValues] = useState({})
  const [recordToDelete, setRecordToDelete] = useState(null)
  const [fieldToDelete, setFieldToDelete] = useState(null)
  const [isDeletingRecord, setIsDeletingRecord] = useState(false)
  const [editingRecordId, setEditingRecordId] = useState(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({})
  const [editFieldErrors, setEditFieldErrors] = useState({})
  const [editError, setEditError] = useState('')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [isOverdueModalOpen, setIsOverdueModalOpen] = useState(false)


  useEffect(() => {
    async function loadFields() {
      try {
        setIsLoading(true)
        setError('')

        const [data, recordsData, overdueData] = await Promise.all([
          getFields(table.id),
          getRecords(table.id),
          getOverdueRecords(table.id),
        ])

        setFields(data)
        setRecords(recordsData)
        setOverdueRecords(overdueData)

        setNewRecordValues(getInitialRecordValues(data))

      } catch (error) {
        setError(error.message)
      } finally {
        setIsLoading(false)
      }
    }

    loadFields()
  }, [table.id])


  useEffect(() => {
    function handleEscape(event) {
      if (event.key !== 'Escape') return

      if (isEditModalOpen && !isUpdatingRecord) {
        handleCancelEdit()
        return
      }

      if (isAddModalOpen && !isAddingRecord) {
        setIsAddModalOpen(false)
        setNewRecordValues(getInitialRecordValues(fields))
        setFieldErrors({})
        setError('')
        return
      }

      if (recordToDelete !== null && !isDeletingRecord) {
        setRecordToDelete(null)
        return
      }

      if (fieldToDelete !== null && !isDeletingField) {
        setFieldToDelete(null)
      }

      if (isOverdueModalOpen) {
        setIsOverdueModalOpen(false)
        return
      }

    }

    window.addEventListener('keydown', handleEscape)

    return () => {
      window.removeEventListener('keydown', handleEscape)
    }
  }, [
    isEditModalOpen,
    isUpdatingRecord,
    isAddModalOpen,
    isAddingRecord,
    isOverdueModalOpen,
    recordToDelete,
    isDeletingRecord,
    fieldToDelete,
    isDeletingField,
    fields,
  ])

  async function handleDeleteField() {
    if (!fieldToDelete) {
      return
    }

    try {
      setIsDeletingField(true)
      await deleteField(table.id, fieldToDelete.id)

      setFields((prevFields) =>
        prevFields.filter((field) => field.id !== fieldToDelete.id)
      )

      setFieldToDelete(null)
      setError('')
    } catch (error) {
      setError(error.message)
    } finally {
      setIsDeletingField(false)
    }
  }

  function getInputType(fieldType) {
    const inputTypes = {
      text: 'text',
      integer: 'number',
      decimal: 'number',
      date: 'date',
      datetime: 'datetime-local',
      phone: 'tel',
      email: 'email',
      url: 'url',
    }

    return inputTypes[fieldType] || 'text'
  }

  function prepareRecordValues(values, fields) {
    const preparedValues = { ...values }

    fields.forEach(field => {
      if (
        field.field_type === 'datetime' &&
        preparedValues[field.name]
      ) {
        preparedValues[field.name] = new Date(
          preparedValues[field.name]
        ).toISOString()
      }
    })

    return preparedValues
  }

  function getFieldHint(field) {
    const hints = []

    // Подсказка в зависимости от типа поля
    switch (field.field_type) {
      case 'text':
        hints.push('Введите текст')
        break

      case 'integer':
        hints.push('Целое число')
        break

      case 'decimal':
        hints.push('Число, можно использовать дробную часть')
        break

      case 'date':
        hints.push('Выберите дату')
        break

      case 'datetime':
        hints.push('Выберите дату и время')
        break

      case 'phone':
        hints.push('Международный формат, например +79991234567')
        break

      case 'email':
        hints.push('Введите адрес, например user@example.com')
        break

      case 'boolean':
        hints.push('Выберите Да или Нет')
        break

      case 'url':
        hints.push('Введите ссылку, например https://example.com')
        break
    }

    // Числовые ограничения
    if (
      field.field_type === 'integer' ||
      field.field_type === 'decimal'
    ) {
      const min = field.settings?.min
      const max = field.settings?.max

      if (min !== undefined && max !== undefined) {
        hints.push(`от ${min} до ${max}`)
      } else if (min !== undefined) {
        hints.push(`не менее ${min}`)
      } else if (max !== undefined) {
        hints.push(`не более ${max}`)
      }
    }

    // Ограничения длины текста
    if (field.field_type === 'text') {
      const minLength = field.settings?.min_length
      const maxLength = field.settings?.max_length

      if (minLength !== undefined && maxLength !== undefined) {
        hints.push(`от ${minLength} до ${maxLength} символов`)
      } else if (minLength !== undefined) {
        hints.push(`не менее ${minLength} символов`)
      } else if (maxLength !== undefined) {
        hints.push(`не более ${maxLength} символов`)
      }
    }

    // Точность десятичного числа
    if (field.field_type === 'decimal') {
      const decimalPlaces = field.settings?.decimal_places

      if (decimalPlaces !== undefined) {
        hints.push(`знаков после запятой: ${decimalPlaces}`)
      }
    }

    // Обязательность поля
    if (!field.required) {
      hints.push('необязательное поле')
    }

    return hints.join(' · ')
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

    if (field.field_type === 'decimal' && value !== '') {
      const decimalPlaces = field.settings?.decimal_places ?? 2

      const parts = value.split('.')

      if (parts.length > 1 && parts[1].length > decimalPlaces) {
        return
      }
    }

    if (field.field_type === 'integer' && value !== '') {
      if (!/^-?\d*$/.test(value)) {
        return
      }
    }

    handleRecordChange(field.name, value)

    if (
      (field.field_type === 'integer' ||
        field.field_type === 'decimal') &&
      value !== '' &&
      Number.isFinite(Number(value))
    ) {
      let rangeError = ''

      const min = field.settings?.min
      const max = field.settings?.max
      const numericValue = Number(value)

      if (min !== undefined && numericValue < Number(min)) {
        rangeError = `Минимальное значение — ${min}.`
      }

      if (max !== undefined && numericValue > Number(max)) {
        rangeError = `Максимальное значение — ${max}.`
      }

      if (rangeError) {
        const updateErrors = prev => ({
          ...prev,
          [field.name]: [rangeError],
        })

        if (editingRecordId !== null) {
          setEditFieldErrors(updateErrors)
        } else {
          setFieldErrors(updateErrors)
        }
      }
    }
      // Проверка диапазона даты и времени

    if (
      (field.field_type === 'date' ||
        field.field_type === 'datetime') &&
      value !== ''
      ) {
      let rangeError = ''

      const min = field.settings?.min
      const max = field.settings?.max

      if (min && value < min) {
        rangeError =
          field.field_type === 'date'
            ? `Дата не может быть раньше ${min}.`
            : `Дата и время не могут быть раньше ${min}.`
      }

      if (max && value > max) {
        rangeError =
          field.field_type === 'date'
            ? `Дата не может быть позже ${max}.`
            : `Дата и время не могут быть позже ${max}.`
      }

      if (rangeError) {
        const updateErrors = prev => ({
          ...prev,
          [field.name]: [rangeError],
        })

        if (editingRecordId !== null) {
          setEditFieldErrors(updateErrors)
        } else {
          setFieldErrors(updateErrors)
        }
      }
    }
  }

  function handleEditRecord(record) {
    setEditingRecordId(record.id)
    const currentFieldNames = new Set(fields.map(field => field.name))

    const currentValues = Object.fromEntries(
      Object.entries(record.values || {}).filter(([fieldName]) =>
        currentFieldNames.has(fieldName)
      )
    )

    setNewRecordValues(currentValues)
    setEditFieldErrors({})
    setEditError('')
    setError('')
    setIsEditModalOpen(true)
  }

  async function handleAddRecord() {
    try {
      setIsAddingRecord(true)

      setError('')
      setFieldErrors({})

      const preparedValues = prepareRecordValues(newRecordValues, fields)

      const newRecord = await createRecord(table.id, preparedValues)

      setRecords([...records, newRecord])
      setNewRecordValues(getInitialRecordValues(fields))
      setIsAddModalOpen(false)

    } catch (error) {
      if (error.details?.values) {
        setFieldErrors(error.details.values)
      } else {
        setError(error.message)
      }
    } finally {
      setIsAddingRecord(false)
    }
  }

  async function handleUpdateRecord() {
    try {
      setIsUpdatingRecord(true)
      setEditFieldErrors({})
      setEditError('')

      const preparedRecord = prepareRecordValues(newRecordValues, fields)

      const updatedRecord = await updateRecord(
        table.id,
        editingRecordId,
        preparedRecord
      )

      setRecords(
        records.map((record) =>
          record.id === editingRecordId
            ? updatedRecord
            : record
        )
      )

      const overdueData = await getOverdueRecords(table.id)
      setOverdueRecords(overdueData)

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
    } finally {
      setIsUpdatingRecord(false)
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

      setIsDeletingRecord(true)
      await deleteRecord(table.id, recordToDelete)

      setRecords(
        records.filter((record) => record.id !== recordToDelete)
      )

      setRecordToDelete(null)
      setError('')
    } catch (error) {
      setError(error.message)
    } finally {
      setIsDeletingRecord(false)
    }
  }

  return (
    <div className="table-detail">
      <button onClick={onBack}>
        Назад к таблицам
      </button>

      <h2>{table.name}</h2>

      {error && <p>{error}</p>}

      {isLoading ? (
          <p>Загрузка данных...</p>
      ) : (
        <>
          {/*<div className="section-heading">*/}
          {/*  <h3>Поля таблицы</h3>*/}

          {/*  <button*/}
          {/*    className="add-button"*/}
          {/*    onClick={() => {*/}
          {/*      setNewFieldName('')*/}
          {/*      setNewFieldLabel('')*/}
          {/*      setNewFieldType('text')*/}
          {/*      setNewFieldRequired(true)*/}
          {/*      setNewFieldSettings({})*/}
          {/*      setError('')*/}
          {/*      setIsAddFieldModalOpen(true)*/}
          {/*    }}*/}
          {/*  >*/}
          {/*    + Добавить поле*/}
          {/*  </button>*/}
          {/*</div>*/}



          {/*{fields.length === 0 ? (*/}
          {/*  <p className="empty-state">В таблице пока нет полей.</p>*/}
          {/*) : (*/}
          {/*  <div className="fields-list">*/}
          {/*    <div className="fields-header">*/}
          {/*      <span>Название поля</span>*/}
          {/*      <span>Тип поля</span>*/}
          {/*      <span>Действия</span>*/}
          {/*    </div>*/}

          {/*    {fields.map((field) => (*/}
          {/*      <div className="field-row" key={field.id}>*/}
          {/*        <span className="field-name">*/}
          {/*          {field.label}*/}
          {/*          {field.required && (*/}
          {/*            <span className="required-mark"> *</span>*/}
          {/*          )}*/}
          {/*        </span>*/}

          {/*        <span className="field-type">*/}
          {/*          {({*/}
          {/*            text: 'Текст',*/}
          {/*            integer: 'Целое число',*/}
          {/*            decimal: 'Десятичное число',*/}
          {/*            date: 'Дата',*/}
          {/*            datetime: 'Дата и время',*/}
          {/*            boolean: 'Да / Нет',*/}
          {/*          })[field.field_type] || field.field_type}*/}
          {/*        </span>*/}

          {/*        <div className="field-actions">*/}
          {/*          <button*/}
          {/*            className="edit-button"*/}
          {/*            title="Редактировать поле"*/}
          {/*            onClick={() => handleEditField(field)}*/}
          {/*          >*/}
          {/*            ✎*/}
          {/*          </button>*/}

          {/*          <button*/}
          {/*            className="delete-button"*/}
          {/*            title="Удалить поле"*/}
          {/*            onClick={() => setFieldToDelete(field)}*/}
          {/*          >*/}
          {/*            ×*/}
          {/*          </button>*/}
          {/*        </div>*/}
          {/*      </div>*/}
          {/*    ))}*/}
          {/*  </div>*/}
          {/*)}*/}

          <button
            className="add-button"
            onClick={() => {
              setNewRecordValues(getInitialRecordValues(fields))
              setFieldErrors({})
              setError('')
              setIsAddModalOpen(true)
            }}
            disabled={fields.length === 0}
          >
            + Добавить запись
          </button>

          <div className="section-heading">
            <h3>Записи таблицы</h3>

            <button
              className="overdue-button"
              onClick={() => setIsOverdueModalOpen(true)}
            >
              Просроченные записи ({overdueRecords.length})
            </button>

          </div>

          {records.length === 0 ? (
            <p>В таблице пока нет записей.</p>
          ) : (
            <div className="table-wrapper">
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
                    <tr
                      key={record.id}
                      className={
                        overdueRecords.some(item => item.id === record.id)
                          ? 'overdue-row'
                          : ''
                      }
                    >
                      {fields.map((field) => (
                        <td key={field.id}>
                          {field.field_type === 'boolean'
                            ? record.values[field.name] === true
                              ? 'Да'
                              : record.values[field.name] === false
                                ? 'Нет'
                                : ''
                            : field.field_type === 'datetime'
                              ? formatDateTime(record.values[field.name])
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
            </div>
          )}

        {isAddModalOpen && (
          <div
            className="modal-overlay"
            onClick={() => {
              if (!isAddingRecord) {
                setIsAddModalOpen(false)
                setNewRecordValues(getInitialRecordValues(fields))
                setFieldErrors({})
                setError('')
              }
            }}
          >
            <div className="modal"
                 onClick={(event) => event.stopPropagation()}
            >
              <h3>Добавление записи</h3>

              <p className="required-hint">
                <span className="required-mark">*</span> — обязательное поле
              </p>

              <div className="record-form modal-record-form">
                {fields.map((field) => (
                  <div className="form-group" key={field.id}>
                    <label>
                      {field.label}
                      {field.required && (
                        <span className="required-mark"> *</span>
                      )}
                    </label>

                    <p className="field-hint">
                      {getFieldHint(field)}
                    </p>

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
                              ? 10 ** -(field.settings?.decimal_places ?? 2)
                              : 1
                        }
                        min={field.settings?.min}
                        max={field.settings?.max}
                        maxLength={
                          field.field_type === 'text'
                            ? field.settings?.max_length
                            : undefined
                        }
                        value={newRecordValues[field.name] ?? ''}
                        className={fieldErrors[field.name] ? 'input-error' : ''}
                        onKeyDown={(event) => {
                          if (
                            field.field_type === 'integer' &&
                            (event.key === '.' || event.key === ',')
                          ) {
                            event.preventDefault()
                          }
                        }}
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
              </div>

              {error && <p className="field-error">{error}</p>}

              <div className="modal-actions">
                <button
                  className="cancel-button"
                  onClick={() => {
                    setIsAddModalOpen(false)
                    setNewRecordValues(getInitialRecordValues(fields))
                    setFieldErrors({})
                    setError('')
                  }}
                >
                  Отмена
                </button>

                <button
                  className="save-button"
                  onClick={handleAddRecord}
                  disabled={isAddingRecord}
                >
                  {isAddingRecord ? 'Добавление...' : 'Добавить'}
                </button>
              </div>
            </div>
          </div>
        )}

        {isEditModalOpen && (
          <div
              className="modal-overlay"
              onClick={() => {
                if (!isUpdatingRecord) {
                  handleCancelEdit()
                }
              }}
          >
            <div
                className="modal"
                onClick={(event) => event.stopPropagation()}>
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
                              ? 10 ** -(field.settings?.decimal_places ?? 2)
                              : `1`
                        }
                        min={field.settings?.min}
                        max={field.settings?.max}
                        maxLength={
                          field.field_type === 'text'
                            ? field.settings?.max_length
                            : undefined
                        }
                        value={newRecordValues[field.name] ?? ''}
                        className={
                          editFieldErrors[field.name] ? 'input-error' : ''
                        }
                        onKeyDown={event => {
                          if (
                            field.field_type === 'integer' &&
                            (event.key === '.' || event.key === ',')
                          ) {
                            event.preventDefault()
                          }
                        }}
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
                  disabled={isUpdatingRecord}
                >
                  {isUpdatingRecord ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </div>
          </div>
        )}

        {isOverdueModalOpen && (
          <div
            className="modal-overlay"
            onClick={() => setIsOverdueModalOpen(false)}
          >
            <div
              className="modal overdue-modal"
              onClick={(event) => event.stopPropagation()}
            >
              <h3>Просроченные записи ({overdueRecords.length})</h3>

              {overdueRecords.length === 0 ? (
                <p className="empty-state">
                  Просроченных записей нет.
                </p>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        {fields.map((field) => (
                          <th key={field.id}>{field.label}</th>
                        ))}
                      </tr>
                    </thead>

                    <tbody>
                      {overdueRecords.map((record) => (
                        <tr key={record.id} className="overdue-row">
                          {fields.map((field) => (
                            <td key={field.id}>
                              {field.field_type === 'boolean'
                                ? record.values[field.name] === true
                                  ? 'Да'
                                  : record.values[field.name] === false
                                    ? 'Нет'
                                    : ''
                                : field.field_type === 'datetime'
                                  ? formatDateTime(record.values[field.name])
                                  : record.values[field.name]}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="modal-actions">
                <button
                  className="cancel-button"
                  onClick={() => setIsOverdueModalOpen(false)}
                >
                  Закрыть
                </button>
              </div>
            </div>
          </div>
        )}


        {recordToDelete !== null && (
          <div
            className="modal-overlay"
            onClick={() => {
              if (!isDeletingRecord) {
                setRecordToDelete(null)
              }
            }}
          >
            <div
              className="modal"
              onClick={(event) => event.stopPropagation()}
            >
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
                  disabled={isDeletingRecord}
                >
                  {isDeletingRecord ? 'Удалить...' : 'Удалить'}
                </button>
              </div>
            </div>
          </div>
        )}

        {fieldToDelete !== null && (
          <div
            className="modal-overlay"
            onClick={() => {
              if (!isDeletingField) {
                setFieldToDelete(null)
              }
            }}
          >
            <div
              className="modal"
              onClick={(event) => event.stopPropagation()}
            >
              <h3>Удаление поля</h3>

              <p>
                Вы действительно хотите удалить поле
                «{fieldToDelete.label}»?
              </p>

              <div className="modal-actions">
                <button
                  className="cancel-button"
                  onClick={() => setFieldToDelete(null)}
                >
                  Отмена
                </button>

                <button
                  className="confirm-button"
                  onClick={handleDeleteField}
                  disabled={isDeletingField}
                >
                  {isDeletingField ? 'Удаление...' : 'Удалить'}
                </button>
              </div>
            </div>
          </div>
        )}

        </>
      )}
    </div>
  )
}

export default TableDetail
