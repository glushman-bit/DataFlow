import { getFields } from '../api/tables'
import { useEffect, useState } from 'react'
import { getTables } from '../api/tables'
import { updateField } from '../api/tables'


function Settings() {
  const [tables, setTables] = useState([])
  const [selectedTableId, setSelectedTableId] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [fields, setFields] = useState([])
  const [fieldsLoading, setFieldsLoading] = useState(false)
  const [fieldsError, setFieldsError] = useState('')
  const [editingField, setEditingField] = useState(null)
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [saveSuccess, setSaveSuccess] = useState('')

  useEffect(() => {
    async function loadTables() {
      try {
        const data = await getTables()
        setTables(data)
      } catch (error) {
        setError('Не удалось загрузить список таблиц.')
      } finally {
        setLoading(false)
      }
    }

    loadTables()
  }, [])

  useEffect(() => {
    if (!selectedTableId) {
      setFields([])
      return
    }

    async function loadFields() {
      setFieldsLoading(true)
      setFieldsError('')

      try {
        const data = await getFields(selectedTableId)
        setFields(data)
      } catch (error) {
        setFieldsError('Не удалось загрузить поля таблицы.')
        setFields([])
      } finally {
        setFieldsLoading(false)
      }
    }

    loadFields()
  }, [selectedTableId])

  const selectedTable = tables.find(
    table => String(table.id) === selectedTableId
  )

  function prepareDateTimeSetting(value) {
    if (!value) return value

    return new Date(value).toISOString()
  }



  async function handleSaveField() {
    setSaving(true)
    setSaveError('')
    setSaveSuccess('')

    if (
      editingField.min !== '' &&
      editingField.max !== '' &&
      Number(editingField.min) > Number(editingField.max)
    ) {
      setSaveError(
        'Минимальное значение не может быть больше максимального.'
      )
      setSaving(false)
      return
    }

    if (
      editingField.field_type === 'text' &&
      editingField.min_length !== '' &&
      editingField.max_length !== '' &&
      Number(editingField.min_length) > Number(editingField.max_length)
    ) {
      setSaveError(
        'Минимальная длина текста не может быть больше максимальной.'
      )
      setSaving(false)
      return
    }

    if (
      editingField.field_type === 'decimal' &&
      (
        editingField.decimal_places === '' ||
        !Number.isInteger(Number(editingField.decimal_places)) ||
        Number(editingField.decimal_places) < 0
      )
    ) {
      setSaveError(
        'Количество знаков после запятой должно быть целым неотрицательным числом.'
      )
      setSaving(false)
      return
    }

    if (
      editingField.field_type === 'integer' &&
      (
        (editingField.min !== '' &&
          !Number.isInteger(Number(editingField.min))) ||
        (editingField.max !== '' &&
          !Number.isInteger(Number(editingField.max)))
      )
    ) {
      setSaveError(
        'Минимальное и максимальное значения должны быть целыми числами.'
      )
      setSaving(false)
      return
    }

    try {
      const settings = {
        ...(editingField.settings || {}),
      }

      if (editingField.min === '') {
        delete settings.min
      } else {
        settings.min = Number(editingField.min)
      }

      if (editingField.max === '') {
        delete settings.max
      } else {
        settings.max = Number(editingField.max)
      }

      if (editingField.field_type === 'decimal') {
        settings.decimal_places = Number(editingField.decimal_places)
      }

      if (editingField.field_type === 'text') {
        if (editingField.min_length === '') {
          delete settings.min_length
        } else {
          settings.min_length = Number(editingField.min_length)
        }

        if (editingField.max_length === '') {
          delete settings.max_length
        } else {
          settings.max_length = Number(editingField.max_length)
        }
      }

      if (
        editingField.field_type === 'date' ||
        editingField.field_type === 'datetime'
      ) {
        if (editingField.min === '') {
          delete settings.min
        } else {
          settings.min =
            editingField.field_type === 'datetime'
              ? prepareDateTimeSetting(editingField.min)
              : editingField.min
        }

        if (editingField.max === '') {
          delete settings.max
        } else {
          settings.max =
            editingField.field_type === 'datetime'
              ? prepareDateTimeSetting(editingField.max)
              : editingField.max
        }

        settings.auto_now = editingField.auto_now
      }

      const updatedField = await updateField(
        selectedTableId,
        editingField.id,
        { settings }
      )

      setFields(prevFields =>
        prevFields.map(field =>
          field.id === updatedField.id ? updatedField : field
        )
      )

      setEditingField(null)
      setSaveSuccess('Настройки поля успешно сохранены.')
    } catch (error) {
      setSaveError('Не удалось сохранить настройки поля.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p>Загрузка таблиц...</p>
  }

  return (
    <div className="settings">
      <h2>Настройки</h2>

      <section className="settings-section">
        <h3>Настройки таблиц</h3>

        {error && <p className="error">{error}</p>}

        {tables.length === 0 ? (
          <p>У вас пока нет созданных таблиц.</p>
        ) : (
          <>
            <label htmlFor="settings-table">
              Выберите таблицу:
            </label>

            <select
              id="settings-table"
              value={selectedTableId}
              onChange={event => setSelectedTableId(event.target.value)}
            >
              <option value="">Выберите таблицу</option>

              {tables.map(table => (
                <option key={table.id} value={table.id}>
                  {table.name}
                </option>
              ))}
            </select>
          </>
        )}

        {selectedTable && (
          <div className="selected-table">
            <h4>{selectedTable.name}</h4>

            <h3>Поля таблицы</h3>

            {fieldsLoading && <p>Загрузка полей...</p>}

            {fieldsError && <p className="error">{fieldsError}</p>}

            {!fieldsLoading && !fieldsError && fields.length === 0 && (
              <p>В этой таблице пока нет полей.</p>
            )}

            {!fieldsLoading && fields.length > 0 && (
              <>
                <div className="settings-fields">
                  {fields.map(field => (
                    <div className="settings-field" key={field.id}>
                      <strong>{field.label}</strong>

                      <p>Тип: {field.field_type}</p>

                      <p>
                        Обязательное:
                        {field.required ? ' Да' : ' Нет'}
                      </p>

                      <button
                        type="button"
                        onClick={() => {
                          setEditingField({
                            ...field,
                            min: field.settings?.min ?? '',
                            max: field.settings?.max ?? '',
                            decimal_places: field.settings?.decimal_places ?? 2,
                            min_length: field.settings?.min_length ?? '',
                            max_length: field.settings?.max_length ?? '',
                            auto_now: field.settings?.auto_now ?? false,
                          })
                          setSaveError('')
                          setSaveSuccess('')
                        }}
                      >
                        Изменить
                      </button>
                    </div>
                  ))}
                </div>

                {editingField && (
                  <div className="edit-field-form">
                    <h3>Настройки поля: {editingField.label}</h3>

                    {(editingField.field_type === 'integer' ||
                      editingField.field_type === 'decimal') && (
                      <>
                        <label>
                          Минимальное значение:
                          <input
                            type="number"
                            value={editingField.min}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                min: event.target.value,
                              })
                            }
                          />
                        </label>

                        <label>
                          Максимальное значение:
                          <input
                            type="number"
                            value={editingField.max}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                max: event.target.value,
                              })
                            }
                          />
                        </label>
                      </>
                    )}

                    {editingField.field_type === 'decimal' && (
                      <label>
                        Количество знаков после запятой:
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={editingField.decimal_places}
                          onChange={event =>
                            setEditingField({
                              ...editingField,
                              decimal_places: event.target.value,
                            })
                          }
                        />
                      </label>
                    )}

                    {editingField.field_type === 'text' && (
                      <>
                        <label>
                          Минимальная длина текста:
                          <input
                            type="number"
                            min="0"
                            step="1"
                            value={editingField.min_length}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                min_length: event.target.value,
                              })
                            }
                          />
                        </label>

                        <label>
                          Максимальная длина текста:
                          <input
                            type="number"
                            min="0"
                            step="1"
                            value={editingField.max_length}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                max_length: event.target.value,
                              })
                            }
                          />
                        </label>
                      </>
                    )}

                    {editingField.field_type === 'date' && (
                      <>
                        <label>
                          Минимальная дата:
                          <input
                            type="date"
                            value={editingField.min}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                min: event.target.value,
                              })
                            }
                          />
                        </label>

                        <label>
                          Максимальная дата:
                          <input
                            type="date"
                            value={editingField.max}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                max: event.target.value,
                              })
                            }
                          />
                        </label>
                      </>
                    )}

                    {editingField.field_type === 'datetime' && (
                      <>
                        <label>
                          Минимальная дата и время:
                          <input
                            type="datetime-local"
                            value={editingField.min}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                min: event.target.value,
                              })
                            }
                          />
                        </label>

                        <label>
                          Максимальная дата и время:
                          <input
                            type="datetime-local"
                            value={editingField.max}
                            onChange={event =>
                              setEditingField({
                                ...editingField,
                                max: event.target.value,
                              })
                            }
                          />
                        </label>
                      </>
                    )}

                    {(editingField.field_type === 'date' ||
                      editingField.field_type === 'datetime') && (
                      <label>
                        <input
                          type="checkbox"
                          checked={editingField.auto_now}
                          onChange={event =>
                            setEditingField({
                              ...editingField,
                              auto_now: event.target.checked,
                            })
                          }
                        />
                        Автоматически подставлять текущую{' '}
                        {editingField.field_type === 'date' ? 'дату' : 'дату и время'}
                      </label>
                    )}

                    <div className="form-actions">
                      <button
                        type="button"
                        onClick={handleSaveField}
                        disabled={saving}
                      >
                        {saving ? 'Сохранение...' : 'Сохранить'}
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          setEditingField(null)
                          setSaveError('')
                        }}
                        disabled={saving}
                      >
                        Отмена
                      </button>
                    </div>

                    {saveError && <p className="error">{saveError}</p>}

                  </div>
                )}

                {saveSuccess && <p className="success">{saveSuccess}</p>}

              </>
            )}

          </div>
        )}
      </section>
    </div>
  )
}

export default Settings

