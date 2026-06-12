import { useState } from 'react';
import { triggerDataUpdate } from '../services/api';

const DataUpdateButton = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleUpdate = async () => {
    setLoading(true);
    setMessage(null);
    setError(null);

    try {
      const result = await triggerDataUpdate();
      setMessage(result.message || 'Data update started successfully');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to trigger data update');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-2">Data Update</h3>
      <p className="text-sm text-gray-600 mb-4">
        Manually trigger the ETL pipeline to fetch the latest crypto data from exchanges.
      </p>
      <button
        onClick={handleUpdate}
        disabled={loading}
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {loading ? 'Starting...' : 'Trigger Data Update'}
      </button>
      {message && (
        <p className="mt-2 text-sm text-green-600">{message}</p>
      )}
      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

export default DataUpdateButton;

