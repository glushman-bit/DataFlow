export async function login(username, password) {
  const response = await fetch('/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: username,
      password: password,
    }),
  })

  if (!response.ok) {
    throw new Error('Неверное имя пользователя или пароль.')
  }

  return response.json()
}


export async function getTables() {
  const response = await apiRequest('/api/tables/')

  if (!response.ok) {
    throw new Error('Не удалось загрузить таблицы.')
  }

  return response.json()
}


export async function createTable(name, description="") {
  const response = await apiRequest('/api/tables/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
      description: description,
    }),
  })

  if (!response.ok) {
    throw new Error('Не удалось создать таблицу.')
  }

  return response.json()
}


export async function deleteTable(tableId) {
  const response = await apiRequest(
    `/api/tables/${tableId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    throw new Error('Не удалось удалить таблицу.')
  }
}


export async function getFields(tableId) {
  const response = await apiRequest(`/api/tables/${tableId}/fields/`)

  if (!response.ok) {
    throw new Error('Не удалось загрузить поля таблицы.')
  }

  return response.json()
}


export async function createField(tableId, fieldData) {
  const response = await apiRequest(`/api/tables/${tableId}/fields/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(fieldData),
  })

  if (!response.ok) {
    throw new Error('Не удалось создать поле.')
  }

  return response.json()
}


export async function updateField(tableId, fieldId, fieldData) {
  const response = await apiRequest(
    `/api/tables/${tableId}/fields/${fieldId}/`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(fieldData),
    }
  )

  if (!response.ok) {
    const errorData = await response.json()

    const errorMessage = Object.entries(errorData)
      .map(([field, messages]) => {
        const text = Array.isArray(messages)
          ? messages.join(' ')
          : String(messages)

        return `${field}: ${text}`
      })
      .join('\n')

    throw new Error(errorMessage || 'Не удалось обновить поле.')
  }

  return response.json()
}


export async function deleteField(tableId, fieldId) {
  const response = await apiRequest(
    `/api/tables/${tableId}/fields/${fieldId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    throw new Error('Не удалось удалить поле.')
  }
}


export async function getRecords(tableId) {
  const response = await apiRequest(`/api/tables/${tableId}/records/`)

  if (!response.ok) {
    throw new Error('Не удалось загрузить записи.')
  }

  return response.json()
}


export async function createRecord(tableId, values) {
  const response = await apiRequest(`/api/tables/${tableId}/records/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      values: values,
    }),
  })


  console.log('Статус ответа:', response.status)
  console.log('Ответ сервера:', response)

  if (!response.ok) {
    await handleApiError(response, 'Не удалось создать запись.')
  }



  return response.json()
}


export async function deleteRecord(tableId, recordId) {
  const response = await apiRequest(
    `/api/tables/${tableId}/records/${recordId}/`,
    {
      method: 'DELETE',
    }
  )

  if (!response.ok) {
    throw new Error('Не удалось удалить запись.')
  }
}


async function handleApiError(response, defaultMessage) {
  const data = await response.json()

  const error = new Error(defaultMessage)
  error.details = data

  throw error
}


export async function updateRecord(tableId, recordId, values) {
  const response = await apiRequest(
    `/api/tables/${tableId}/records/${recordId}/`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        values: values,
      }),
    }
  )

  if (!response.ok) {
    await handleApiError(response, 'Не удалось обновить запись.')
  }

  return response.json()
}


export async function refreshAccessToken() {
  const refresh = localStorage.getItem('refresh')

  const response = await fetch('/api/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      refresh: refresh,
    }),
  })

  if (!response.ok) {
    throw new Error('Не удалось обновить токен.')
  }

  const data = await response.json()

  localStorage.setItem('access', data.access)

  return data.access
}


async function apiRequest(url, options = {}) {
  let token = localStorage.getItem('access')

  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  })

  if (response.status === 401) {
    token = await refreshAccessToken()

    response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${token}`,
      },
    })
  }

  return response
}
