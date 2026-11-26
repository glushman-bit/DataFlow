import { getFields, getTables, updateField, createField, deleteField } from '../api/tables'
import { useEffect, useState } from 'react'


function generateFieldName(label) {
  const transliteration = {
    а: 'a', б: 'b', в: 'v', г: 'g', д: 'd',
    е: 'e', ё: 'yo', ж: 'zh', з: 'z', и: 'i',
    й: 'y', к: 'k', л: 'l', м: 'm', н: 'n',
    о: 'o', п: 'p', р: 'r', с: 's', т: 't',
    у: 'u', ф: 'f', х: 'h', ц: 'ts', ч: 'ch',
    ш: 'sh', щ: 'sch', ъ: '', ы: 'y', ь: '',
    э: 'e', ю: 'yu', я: 'ya',
  }

  return label
    .toLowerCase()
    .split('')
    .map(char => transliteration[char] ?? char)
    .join('')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '')
}


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

  const [isAddFieldOpen, setIsAddFieldOpen] = useState(false)
  const [isAddingField, setIsAddingField] = useState(false)
  const [newFieldName, setNewFieldName] = useState('')
  const [newFieldLabel, setNewFieldLabel] = useState('')
  const [newFieldType, setNewFieldType] = useState('text')
  const [newFieldRequired, setNewFieldRequired] = useState(true)
  const [newFieldSettings, setNewFieldSettings] = useState({})


  useEffect(() => {
    async function loadTables() {
      try {
        const data = await getTables()
        setTables(data)
      } catch {
        setError('Не удалось загрузить список таблиц.')
      } finally {
        setLoading(false)
      }
    }

    loadTables()
  }, [])

  useEffect(() => {

    if (!selectedTableId) {
      return
    }

    async function loadFields() {
      setFieldsLoading(true)
      setFieldsError('')

      try {
        const data = await getFields(selectedTableId)
        setFields(data)
      } catch {
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
      setIsAddingField(true)
      setSaveError('')
      setSaveSuccess('')

      const newField = await createField(selectedTableId, fieldData)

      setFields(prevFields => [...prevFields, newField])
      setNewFieldName('')
      setNewFieldLabel('')
      setNewFieldType('text')
      setNewFieldRequired(true)
      setNewFieldSettings({})
      setIsAddFieldOpen(false)
      setSaveSuccess('Поле успешно добавлено.')
    } catch (error) {
      const details = error.details

      if (details?.name || details?.label) {
        const messages = [
          ...(details.name || []),
          ...(details.label || []),
        ]

        setSaveError(messages.join(' '))
      } else {
        setSaveError(error.message || 'Не удалось добавить поле.')
      }
    } finally {
      setIsAddingField(false)
    }
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

        const deadline = {
          ...(editingField.settings?.deadline || {}),
          enabled: editingField.deadline_enabled,
        }

        if (deadline.enabled) {
          settings.deadline = deadline
        } else {
          delete settings.deadline
        }
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
    } catch {
      setSaveError('Не удалось сохранить настройки поля.')
    } finally {
      setSaving(false)
    }
  }


  async function handleDeleteField(field) {
    const confirmed = window.confirm(
      `Удалить поле «${field.label}»?`
    )

    if (!confirmed) return

    try {
      setSaveError('')
      setSaveSuccess('')

      await deleteField(selectedTableId, field.id)

      setFields(prevFields =>
        prevFields.filter(item => item.id !== field.id)
      )

      if (editingField?.id === field.id) {
        setEditingField(null)
      }

      setSaveSuccess('Поле успешно удалено.')
    } catch (error) {
      setSaveError(error.message || 'Не удалось удалить поле.')
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
              onChange={event => {
                setFields([])
                setSelectedTableId(event.target.value)
              }}
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

            <button
              type="button"
              onClick={() => {
                setIsAddFieldOpen(true)
                setSaveError('')
                setSaveSuccess('')
              }}
            >
              Добавить поле
            </button>

            {isAddFieldOpen && (
              <div className="edit-field-form">
                <h3>Добавление поля</h3>

                {saveError && <p className="error">{saveError}</p>}

                <input
                  type="text"
                  placeholder="Название поля (например, Клиент)"
                  value={newFieldLabel}
                  onChange={event => {
                    const value = event.target.value

                    setNewFieldLabel(value)
                    setNewFieldName(generateFieldName(value))
                  }}
                />

                <select
                  value={newFieldType}
                  onChange={event => {
                    setNewFieldType(event.target.value)
                    setNewFieldSettings({})
                  }}
                >
                  <option value="text">Текст</option>
                  <option value="integer">Целое число</option>
                  <option value="decimal">Десятичное число</option>
                  <option value="date">Дата</option>
                  <option value="datetime">Дата и время</option>
                  <option value="phone">Номер телефона</option>
                  <option value="email">Электронная почта</option>
                  <option value="boolean">Да / Нет</option>
                  <option value="url">Ссылка</option>
                </select>

                <label>
                  <input
                    type="checkbox"
                    checked={newFieldRequired}
                    onChange={event => setNewFieldRequired(event.target.checked)}
                  />
                  Обязательное поле
                </label>

                <div className="form-actions">
                  <button
                    type="button"
                    onClick={handleAddField}
                    disabled={isAddingField}
                  >
                    {isAddingField ? 'Добавление...' : 'Добавить'}
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setIsAddFieldOpen(false)
                      setSaveError('')
                    }}
                    disabled={isAddingField}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            )}

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
                      <div className="settings-field-header">
                        <div>
                          <strong>{field.label}</strong>
                          <p>Тип: {field.field_type}</p>
                          <p>
                            Обязательное: {field.required ? 'Да' : 'Нет'}
                          </p>
                        </div>

                        <div className="settings-field-actions">
                          {editingField?.id === field.id ? (
                            <button
                              type="button"
                              title="Закрыть редактирование"
                              aria-label="Закрыть редактирование"
                              onClick={() => {
                                setEditingField(null)
                                setSaveError('')
                              }}
                            >
                              ✖
                            </button>
                          ) : (
                            <>
                              <button
                                type="button"
                                title="Редактировать поле"
                                aria-label="Редактировать поле"
                                onClick={() => {
                                  setEditingField({
                                    ...field,
                                    min: field.settings?.min ?? '',
                                    max: field.settings?.max ?? '',
                                    decimal_places: field.settings?.decimal_places ?? 2,
                                    min_length: field.settings?.min_length ?? '',
                                    max_length: field.settings?.max_length ?? '',
                                    auto_now: field.settings?.auto_now ?? false,
                                    deadline_enabled: field.settings?.deadline?.enabled ?? false,
                                  })
                                  setSaveError('')
                                  setSaveSuccess('')
                                }}
                              >
                                ✎
                              </button>

                              <button
                                type="button"
                                title="Удалить поле"
                                aria-label="Удалить поле"
                                onClick={() => handleDeleteField(field)}
                              >
                                🗑️
                              </button>
                            </>
                          )}
                        </div>

                      </div>

                      {editingField?.id === field.id && (
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

                          {(editingField.field_type === 'date' ||
                            editingField.field_type === 'datetime') && (
                            <label>
                              <input
                                type="checkbox"
                                checked={editingField.deadline_enabled}
                                onChange={event =>
                                  setEditingField({
                                    ...editingField,
                                    deadline_enabled: event.target.checked,
                                  })
                                }
                              />
                              Контроль срока (отслеживать просроченные записи)
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
                    </div>
                  ))}
                </div>

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

