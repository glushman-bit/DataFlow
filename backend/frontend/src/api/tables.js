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
  const response = await fetch('/api/tables/', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Не удалось загрузить таблицы.')
  }

  return response.json()
}


export async function createTable(name, token) {
  const response = await fetch('/api/tables/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
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