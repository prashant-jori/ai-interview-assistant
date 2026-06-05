import { useEffect, useState } from "react";
import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

function Analytics() {

  const [results, setResults] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    average: 0,
    best: 0
  });

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = async () => {

    try {

      const res = await axios.get(
        "http://127.0.0.1:5000/results-history"
      );

      setResults(res.data);

      if (res.data.length > 0) {

        const scores = res.data.map(
          item => item.score || 0
        );

        const avg =
          scores.reduce((a, b) => a + b, 0) /
          scores.length;

        setStats({
          total: scores.length,
          average: avg.toFixed(2),
          best: Math.max(...scores)
        });
      }

    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div>

      <h2 className="mb-4">
        Analytics Dashboard 📊
      </h2>

      <div className="row">

        <div className="col-md-4">
          <div className="card p-3 shadow">
            <h5>Total Tests</h5>
            <h2>{stats.total}</h2>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card p-3 shadow">
            <h5>Average Score</h5>
            <h2>{stats.average}</h2>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card p-3 shadow">
            <h5>Best Score</h5>
            <h2>{stats.best}</h2>
          </div>
        </div>

      </div>

      <div
        className="mt-5"
        style={{ width: "100%", height: 400 }}
      >

        <ResponsiveContainer>

          <LineChart data={results}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="id" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="score"
              stroke="#8884d8"
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}

export default Analytics;