
function TableDetail({ table, onBack }) {
  return (
    <div className="table-detail">
      <button onClick={onBack}>
        Назад к таблицам
      </button>

      <h2>{table.name}</h2>

      <p>Здесь будут поля и записи выбранной таблицы.</p>
    </div>
  )
}

export default TableDetail
