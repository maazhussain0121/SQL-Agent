function ResultsTable({ data }) {
  if (!Array.isArray(data)) {
    return <div className="table-error">{String(data)}</div>;
  }

  if (data.length === 0) {
    return <div className="empty-results">No records found.</div>;
  }

  const columns = Object.keys(data[0] || {});

  return (
    <div className="results-table-wrap">
      <table className="results-table">
        <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => <td key={column}>{row[column] === null ? "-" : String(row[column])}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ResultsTable;
