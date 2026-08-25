import { useEffect, useState } from "react";

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchJobs() {
      try {
        const response = await fetch("http://127.0.0.1:8000/jobs");

        if (!response.ok) {
          throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        setJobs(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    fetchJobs();
  }, []);

  if (loading) {
    return <p>Loading jobs...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <main>
      <h1>Tech Job Analytics</h1>

      {jobs.map((job) => (
        <article key={job.id}>
          <h2>{job.title}</h2>

          <p>
            <strong>Company:</strong> {job.company_name}
          </p>

          <p>
            <strong>Location:</strong> {job.location_name}
          </p>

          <p>
            <strong>Salary:</strong> {job.salary_min} - {job.salary_max}
          </p>

          <p>{job.description}</p>
        </article>
      ))}
    </main>
  );
}

export default App;