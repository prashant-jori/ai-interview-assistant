function Dashboard() {
  return (
    <div className="container mt-5">
      <h2>AI Interview Assistant Dashboard 🚀</h2>

      <div className="mt-4">
        <button className="btn btn-primary m-2">
          Upload PDF
        </button>

        <button className="btn btn-success m-2">
          Generate Questions
        </button>

        <button className="btn btn-warning m-2">
          Voice Interview
        </button>

        <button className="btn btninfo m-2">
          Results History
        </button>

        <button className="btn btn-dark m-2">
          Analytics
        </button>
      </div>
    </div>
  );
}

export default Dashboard;