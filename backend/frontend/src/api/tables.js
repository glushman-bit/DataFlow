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


export async function getTables(token) {
  const response = await apiRequest('/api/tables/')

  if (!response.ok) {
    throw new Error('Не удалось загрузить таблицы.')
  }

  return response.json()
}


export async function createTable(name, token) {
  const response = await apiRequest('/api/tables/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name,
    }),
  })

  if (!response.ok) {
    throw new Error('Не удалось создать таблицу.')
  }

  return response.json()
}


export async function getFields(tableId, token) {
  const response = await apiRequest(`/api/tables/${tableId}/fields/`)

  if (!response.ok) {
    throw new Error('Не удалось загрузить поля таблицы.')
  }

  return response.json()
}


export async function createField(tableId, fieldData, token) {
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


export async function getRecords(tableId, token) {
  const response = await apiRequest(`/api/tables/${tableId}/records/`)

  if (!response.ok) {
    throw new Error('Не удалось загрузить записи.')
  }

  return response.json()
}


export async function createRecord(tableId, values, token) {
  const response = await apiRequest(`/api/tables/${tableId}/records/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      values: values,
    }),
  })

  if (!response.ok) {
    throw new Error('Не удалось создать запись.')
  }

  return response.json()
}


export async function deleteRecord(tableId, recordId, token) {
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
